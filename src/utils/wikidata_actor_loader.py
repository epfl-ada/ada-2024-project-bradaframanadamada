from SPARQLWrapper import SPARQLWrapper, JSON
import time
import pandas as pd
import requests
from tqdm import tqdm
from clean_country import country_mapping

class WikiDataActorLoader:
    """
    Class used to load the Wikidata of actors and extract as much information as possible.
    """

    def __init__(self):
        # Define SPARQL endpoint and query template
        self.SPARQL_ENDPOINT = "https://query.wikidata.org/sparql"
        self.STEP = 100
        self.MAX_RETRIES = 7  # Maximum number of retries on failure
        self.RETRY_DELAY = 2  # Delay in seconds between retries
        self.DELAY_FACTOR = 2  # Factor to multiply to have an exponential delay when retrying
        self.USER_AGENT = "Agent/1.0"


    def fetch_actors(self, freebase_ids):
        """
        Function to fetch actor data in batches with retry on failure.

        :param offset: the offset used for the query.
        """
        query = f"""
            SELECT ?actor ?actorLabel ?birth_date ?death_date ?genderLabel ?imdb_id ?freebase_id 
                (GROUP_CONCAT(DISTINCT ?nationalityLabel; separator=", ") AS ?nationalitie_Lst)
                (GROUP_CONCAT(DISTINCT ?occupationLabel; separator=", ") AS ?occupation_Lst)
                (GROUP_CONCAT(DISTINCT ?spouseLabel; separator=", ") AS ?spouse_Lst)
                (GROUP_CONCAT(DISTINCT ?childrenLabel; separator=", ") AS ?children_Lst)
                (GROUP_CONCAT(DISTINCT ?alma_materLabel; separator=", ") AS ?almaMater_Lst)
                (GROUP_CONCAT(DISTINCT ?award_receivedLabel; separator=", ") AS ?award_received_Lst)
                ?wikidata_id
            WHERE {{
                ?actor wdt:P31 wd:Q5;                      # Instance of "human"
                    wdt:P106 wd:Q33999;                 # Occupation "actor"
                    wdt:P646 ?freebase_id.              # Freebase ID

                # Filter by the list of Freebase IDs given in argument.
                VALUES ?freebase_id {{ {" ".join(f'"{id}"' for id in freebase_ids)} }}

                # The actor label
                OPTIONAL {{ 
                    ?actor rdfs:label ?actorLabel. 
                    FILTER (LANG(?actorLabel) = "en") 
                }}
                # Birth date
                OPTIONAL {{ ?actor wdt:P569 ?birth_date. }}
                # Death date           
                OPTIONAL {{ ?actor wdt:P570 ?death_date. }} 
                # Gender          
                OPTIONAL {{ 
                    ?actor wdt:P21 ?gender. 
                    ?gender rdfs:label ?genderLabel. 
                    FILTER (LANG(?genderLabel) = "en")
                }}                
                 # Nationality
                OPTIONAL {{ 
                    ?actor wdt:P27 ?nationality.
                    ?nationality rdfs:label ?nationalityLabel. 
                    FILTER (LANG(?nationalityLabel) = "en") 
                }}          
                # Occupation
                OPTIONAL {{ 
                    ?actor wdt:P106 ?occupation.
                    ?occupation rdfs:label ?occupationLabel. 
                    FILTER (LANG(?occupationLabel) = "en")
                }}
                # Spouse
                OPTIONAL {{ 
                    ?actor wdt:P26 ?spouse. 
                    ?spouse rdfs:label ?spouseLabel. 
                    FILTER (LANG(?spouseLabel) = "en")
                }} 
                # Children               
                OPTIONAL {{ 
                    ?actor wdt:P40 ?children. 
                    ?children rdfs:label ?childrenLabel. 
                    FILTER (LANG(?childrenLabel) = "en")
                }}
                # University attended
                OPTIONAL {{ 
                    ?actor wdt:P69 ?alma_mater.
                    ?alma_mater rdfs:label ?alma_materLabel. 
                    FILTER (LANG(?alma_materLabel) = "en")
                }}            
                # Awards received   
                OPTIONAL {{ 
                    ?actor wdt:P166 ?award_received.
                    ?award_received rdfs:label ?award_receivedLabel. 
                    FILTER (LANG(?award_receivedLabel) = "en") 
                }}  
                # IMDB ID      
                OPTIONAL {{ ?actor wdt:P345 ?imdb_id. }}                           
            }}
            GROUP BY ?actor ?actorLabel ?birth_date ?death_date ?genderLabel ?imdb_id ?freebase_id ?wikidata_id
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
                response = sparql.query().convert()  # Execute the query
                return (response, None)
                
            except Exception as e:
                print(e)
                if attempt < self.MAX_RETRIES - 1:
                    time.sleep(delay)
                    delay = delay * self.DELAY_FACTOR
                else:
                    print("Max retries reached, skipping this batch.")
                    return (None, freebase_ids)  # Return None if all retries fail

    def load_wikidata(self, fileName, freebase_IDs):
        """
        Function used to load the Wikidata with all the actors present and save the result into a CSV file.

        :param fileName: the name of the CSV file where the data will be saved.
        """
        
        # Initialize storage for data
        all_data = []
        failed_IDs = []
        steps = range(0, len(freebase_IDs), self.STEP)
        for interStep in tqdm(range(0, len(freebase_IDs), self.STEP), desc="Processing Freebase IDs"):
            nextStep = min(interStep + self.STEP, len(freebase_IDs))
            inter_freebase_IDs = freebase_IDs[interStep:nextStep]

            # Fetch data interStep
            data = self.fetch_actors(freebase_ids=inter_freebase_IDs)
            if data[0] is None:
                print(f"Failed to retrieve data due to repeated errors from {interStep} to {nextStep - 1}.")
                failed_IDs.extend(data[1])  # Return empty list to avoid NoneType issues
            # Extract and store results
            results = data[0].get("results", {}).get("bindings", [])
            if not results:
                print(f"No results for this batch, skipping from {interStep} to {nextStep - 1}.")

            # Process each result and store it as a dictionary
            for result in results:
                actor = {
                    "actor": result["actor"]["value"],
                    "actorLabel": result.get("actorLabel", {}).get("value"),
                    "birth_date": result.get("birth_date", {}).get("value"),
                    "death_date": result.get("death_date", {}).get("value"),
                    "gender": result.get("genderLabel", {}).get("value"),
                    "imdb_id": result.get("imdb_id", {}).get("value"),
                    "freebase_id": result.get("freebase_id", {}).get("value"),
                    "nationality": result.get("nationalitie_Lst", {}).get("value"),
                    "occupation": result.get("occupation_Lst", {}).get("value"),
                    "spouse": result.get("spouse_Lst", {}).get("value"),
                    "children": result.get("children_Lst", {}).get("value"),
                    "alma_mater": result.get("almaMater_Lst", {}).get("value"),
                    "award_received": result.get("award_received_Lst", {}).get("value"),
                    "wikidata_id": result.get("actor", {}).get("value").split("/")[-1]  # Extract Wikidata ID
                }
                all_data.append(actor)

        # Convert data to a DataFrame and save as CSV
        df = pd.DataFrame(all_data)
        df.to_csv(f"{fileName}.csv", index=False)
        print(f"Data saved to '{fileName}.csv'")
        print(f"Failed Ids : {failed_IDs}")
        return failed_IDs
    
    def clean_file_data(self, fileName, newFileName):
        """
        Clean the data that contains the actors data.

        :param fileName: the name of the file that contains the ators data.
        :param newFileName: the name of the csv file whre the clean will be saved.
        :return: the clean dataframe.
        """
        df_data_not_clean = pd.read_csv(fileName)
        
        # remove empty columns
        for column in df_data_not_clean.columns:
            if(df_data_not_clean[column].isna().all()):
                df_data_not_clean.drop(columns = [column], inplace = True)

        # change string encoding list to a list of elements
        for column in ['nationality', 'occupation',	'spouse', 'children', 'alma_mater',	'award_received']:
            df_data_not_clean[column] = df_data_not_clean[column].apply(
                lambda x: list(x.split(', ')) if isinstance(x, str) else list()
            )
            
        # clean the nationality list
        df_data_not_clean['nationality'] = df_data_not_clean['nationality'].apply(lambda x: [country_mapping.get(elem) for elem in x])

        # save the data clean
        df_data_not_clean.to_csv(f"{newFileName}.csv", index=False)
        return df_data_not_clean
