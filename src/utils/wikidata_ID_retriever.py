from SPARQLWrapper import SPARQLWrapper, JSON
import time

class WikidataIDRetriever:
        """
        Class used to retrieve a Wikidata ID from a freebase ID.
        """
        def __init__(self):
            self.sparQuery = SPARQLWrapper("https://query.wikidata.org/sparql")
            self.sparQuery.setReturnFormat(JSON)

        def retrieve_wikidata_ID(self, freebase_ID):
            """
            Function used to retrive a Wikidata ID from a given freebase ID.

            :param freebase_ID: the freebase ID that w want to convert to potential wikidata ID.
            :return: The Wikidata ID if it exist, otherwise None.
            """

            # the query used to find the wikidata IDs
            query = f"""
            SELECT ?wikidataID WHERE {{
                ?wikidataID wdt:P646 "{freebase_ID}" .
            }}
            """

            self.sparQuery.setQuery(query)
            try:
                # obtains the query's results
                queryResults = self.sparQuery.query().convert()

                # extract the wikidata ID from the results
                results_linked = queryResults.get("results", {}).get("bindings", [])
                if results_linked:
                        # extract the wikidata ID part
                        return results_linked[0]['wikidataID']['value'].split("/")[-1] 
                else:
                        # no wikidata ID was found
                        return None
            except Exception as error:
                  print(f"Error when retrieving wikidata ID for : {freebase_ID} : {error}")
            
            time.sleep(1)