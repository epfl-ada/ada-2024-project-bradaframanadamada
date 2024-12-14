from SPARQLWrapper import SPARQLWrapper, JSON
import time
import pandas as pd
import requests
from tqdm import tqdm

class WikiDataCharacterLoader:
    """
    Class used to load the Wikidata of characters and extract as much information as possible.
    """

    def __init__(self):
        # Define SPARQL endpoint and query template
        self.SPARQL_ENDPOINT = "https://query.wikidata.org/sparql"
        self.STEP = 200 # Number of data retrieve at each step
        self.MAX_RETRIES = 7  # Maximum number of retries on failure
        self.RETRY_DELAY = 2  # Delay in seconds between retries
        self.DELAY_FACTOR = 2  # Factor to multiply to have an exponential delay when retrying
        self.USER_AGENT = "Agent/1.0"


    def fetch_characters(self, freebase_ids):
        """
        Function to fetch characters data with retry on failure.

        :param offset: the offset used for the query.
        :param freebase_ids: the list of freebase IDs of the character that we would like to retrieve on the wikidata.
        """
        query = f"""
        SELECT ?character ?characterLabel ?freebase_id
            (GROUP_CONCAT(DISTINCT ?occupationLabel; separator=", ") AS ?occupation_Lst)
            (GROUP_CONCAT(DISTINCT ?powersLabel; separator=", ") AS ?powers_Lst)
            (GROUP_CONCAT(DISTINCT ?affiliationLabel; separator=", ") AS ?affiliation_Lst)
            (GROUP_CONCAT(DISTINCT ?speciesLabel; separator=", ") AS ?species_Lst)
            (GROUP_CONCAT(DISTINCT ?alliesLabel; separator=", ") AS ?allies_Lst)
            (GROUP_CONCAT(DISTINCT ?enemiesLabel; separator=", ") AS ?enemies_Lst)
        WHERE {{
            ?character wdt:P646 ?freebase_id.                 # Freebase ID

            # Filter by the list of Freebase IDs given in argument.
            VALUES ?freebase_id {{ {" ".join(f'"{id}"' for id in freebase_ids)} }}

            # The character label
            OPTIONAL {{ 
                ?character rdfs:label ?characterLabel. 
                FILTER (LANG(?characterLabel) = "en") 
            }}          
            # Occupation or role (e.g., superhero, villain, etc.)
            OPTIONAL {{ 
                ?character wdt:P106 ?occupation.
                ?occupation rdfs:label ?occupationLabel. 
                FILTER (LANG(?occupationLabel) = "en")
            }}
            # Powers/abilities (if defined for the character)
            OPTIONAL {{ 
                ?character wdt:P1012 ?powers. 
                ?powers rdfs:label ?powersLabel. 
                FILTER (LANG(?powersLabel) = "en")
            }}
            # Affiliation (team or organization, if relevant)
            OPTIONAL {{ 
                ?character wdt:P463 ?affiliation. 
                ?affiliation rdfs:label ?affiliationLabel. 
                FILTER (LANG(?affiliationLabel) = "en")
            }}
            # Species or race (if defined for the character)
            OPTIONAL {{ 
                ?character wdt:P141 ?species. 
                ?species rdfs:label ?speciesLabel. 
                FILTER (LANG(?speciesLabel) = "en")
            }}
            # Allies (other characters or teams)
            OPTIONAL {{ 
                ?character wdt:P40 ?allies. 
                ?allies rdfs:label ?alliesLabel. 
                FILTER (LANG(?alliesLabel) = "en")
            }}
            # Enemies (antagonists or rival characters)
            OPTIONAL {{ 
                ?character wdt:P2846 ?enemies. 
                ?enemies rdfs:label ?enemiesLabel. 
                FILTER (LANG(?enemiesLabel) = "en")
            }}                        
        }}
        GROUP BY ?character ?characterLabel ?freebase_id ?wikidata_id
        LIMIT {len(freebase_ids)}
    """

        
        # Use SPARQLWrapper to query the endpoint
        sparql = SPARQLWrapper(self.SPARQL_ENDPOINT)
        sparql.setQuery(query)
        sparql.setReturnFormat(JSON)
        sparql.addCustomHttpHeader("User-Agent", self.USER_AGENT)
        
        
        delay = self.RETRY_DELAY
        for attempt in range(self.MAX_RETRIES):
            try:
                response = sparql.query().convert()
                return (response, None)
                
            except Exception as e:
                print(e)
                if attempt < self.MAX_RETRIES - 1:
                    time.sleep(delay)
                    delay = delay * self.DELAY_FACTOR
                else:
                    print("Max retries reached, skipping this batch.")
                    # Return None if all retries fail
                    return (None, freebase_ids) 
                
    def load_wikidata(self, fileName, freebase_IDs):
        """
        Function used to load the Wikidata with all the actors present and save the result into a CSV file.

        :param fileName: the name of the CSV file where the data will be saved.
        :param freebase_ids: the list of freebase IDs of the character that we would like to retrieve on the wikidata.
        """
        
        # Initialize the stack to store the results.
        all_data = []
        failed_IDs = []
        steps = range(0, len(freebase_IDs), self.STEP)
        for interStep in tqdm(range(0, len(freebase_IDs), self.STEP), desc="Processing Freebase IDs"):
            nextStep = min(interStep + self.STEP, len(freebase_IDs))
            inter_freebase_IDs = freebase_IDs[interStep:nextStep]

            # Fetch data interStep
            data = self.fetch_characters(freebase_ids=inter_freebase_IDs)
            if data[0] is None:
                print(f"Failed to retrieve data due to repeated errors from {interStep} to {nextStep - 1}.")
                failed_IDs.extend(data[1])  # Return empty list to avoid NoneType issues
            # Extract and store results
            results = data[0].get("results", {}).get("bindings", [])

            # Process each result and store it as a dictionary
            for result in results:
                character = {
                    "character": result["character"]["value"], 
                    "characterLabel": result.get("characterLabel", {}).get("value"),
                    "freebase_id": result.get("freebase_id", {}).get("value"), 
                    "powers": result.get("powers_Lst", {}).get("value"), 
                    "occupation": result.get("occupation_Lst", {}).get("value"), 
                    "affiliation": result.get("affiliation_Lst", {}).get("value"),
                    "species": result.get("species_Lst", {}).get("value"), 
                    "allies": result.get("allies_Lst", {}).get("value"), 
                    "wikidata_id": result["character"]["value"].split("/")[-1]  # Extract Wikidata ID
                }
                all_data.append(character)

        # Convert data to a DataFrame and save as CSV
        df = pd.DataFrame(all_data)
        df.to_csv(f"{fileName}.csv", index=False)
        print(f"Data saved to '{fileName}.csv'")
        print(f"Failed Ids : {failed_IDs}")
        return failed_IDs
    
    def clean_file_data(self, fileName, newFileName):
        """
        Clean the data that contains the characters data.

        :param fileName: the name of the file that contains the character data.
        :param newFileName: the name of the csv file where the clean will be saved.
        :return: the clean dataframe.
        """
        df_data_not_clean = pd.read_csv(fileName)

        # Print the initial number of elements
        print(f'Initial number of elements : {df_data_not_clean.shape[0]}')

        # remove empty columns
        for column in df_data_not_clean.columns:
            if(df_data_not_clean[column].isna().all()):
                df_data_not_clean.drop(columns = [column], inplace = True)

        # change string encoding list to a list of elements
        for column in ['occupation', 'affiliation',	'allies']:
            df_data_not_clean[column] = df_data_not_clean[column].apply(
                lambda x: list(x.split(', ')) if isinstance(x, str) else x
            )

        duplicates = df_data_not_clean[df_data_not_clean.duplicated(subset=["freebase_id"], keep=False)]

        # Show the duplicated elements
        print(f'Number of duplicated elements: {duplicates.shape[0]}')
        for key, elems in duplicates.groupby('freebase_id'):
            print(f"For the freebase id {key} differences between:")
            print(elems)
            print("\n***********************************************\n")

        # These duplicates can be explained by the fact that a freebase id can point to different wikipedia pages.
        # We will join this duplicates
        grou_by_data_not_clean = df_data_not_clean.groupby(['freebase_id']).agg({
            'characterLabel': lambda x: list(set([elem for elem in x if isinstance(elem, str)])),
            'occupation': lambda x: list(set([elem for sublist in x if isinstance(sublist, list) for elem in sublist])),
            'affiliation': lambda x: list(set([elem for sublist in x if isinstance(sublist, list) for elem in sublist])),
            'allies': lambda x: list(set([elem for sublist in x if isinstance(sublist, list) for elem in sublist])),
            'wikidata_id': lambda x: list(set([elem for elem in x if isinstance(elem, str)]))
        }).reset_index()
        # Check the number of duplicated elements
        duplicates = grou_by_data_not_clean[grou_by_data_not_clean.duplicated(subset=["freebase_id"], keep=False)]
        print(f'Number of duplicated elements after cleaning: {len(duplicates)}')

        # rename the columns
        grou_by_data_not_clean = grou_by_data_not_clean.rename(columns={'characterLabel': 'character_name_lst',
                                                                        'occupation': 'occupation_lst',
                                                                        'affiliation': 'affiliation_lst',
                                                                        'allies': 'allies_lst',
                                                                        'wikidata_id': 'wikidata_id_lst'})
        # only keep the useful elements
        grou_by_data_not_clean = grou_by_data_not_clean[['freebase_id',
                                                         'character_name_lst',
                                                         'occupation_lst',
                                                         'affiliation_lst',
                                                         'allies_lst',
                                                         'wikidata_id_lst']]

        # Print the number of elements after the cleaning process
        print(f'Number of elements after cleaning: {grou_by_data_not_clean.shape[0]}')

        # save the data clean
        grou_by_data_not_clean.to_csv(f"{newFileName}", index=False)
        return grou_by_data_not_clean

