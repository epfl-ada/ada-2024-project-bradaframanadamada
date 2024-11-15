import pandas as pd
import time
import requests


SPARQL_ENDPOINT = "https://query.wikidata.org/sparql"
BATCH_SIZE = 5000
OFFSET = 0
MAX_RETRIES = 20
RETRY_DELAY = 2
DELAY_FACTOR = 2

def fetch_movies_in_batches(offset):
    query = f"""
    SELECT ?item ?itemLabel ?imdb_id ?freebase_id ?budget ?award_received ?award_receivedLabel ?nominated_for ?nominated_forLabel
    WHERE {{
        # Fetch items that are an instance of "film" or any subclass of "film"
        ?item wdt:P31/wdt:P279* wd:Q11424.

        # Required properties
        ?item  wdt:P345 ?imdb_id.
        ?item  wdt:P646 ?freebase_id.

        # Optional properties
        OPTIONAL {{ ?item wdt:P2130 ?budget. }}
        OPTIONAL {{ ?item wdt:P166 ?award_received. }}
        OPTIONAL {{ ?item wdt:P1411 ?nominated_for. }}
      
      SERVICE wikibase:label {{ bd:serviceParam wikibase:language "[AUTO_LANGUAGE],en". }}
    }}
    ORDER BY ?freebase_id
    LIMIT {BATCH_SIZE} OFFSET {offset}
    """
    
    headers = {
        "User-Agent": "Python SPARQL batch downloader",
        "Accept": "application/sparql-results+json"
    }

    delay = RETRY_DELAY
    for attempt in range(MAX_RETRIES):
        try:
            response = requests.get(SPARQL_ENDPOINT, params={'query': query}, headers=headers)
            response.raise_for_status()
            return response.json()
        
        except requests.exceptions.RequestException as e:
            print(f"Error on attempt {attempt + 1} for OFFSET {offset}: {e}")
            if attempt < MAX_RETRIES - 1:
                print(f"Retrying in {delay} seconds...")
                time.sleep(delay)
                delay = delay * DELAY_FACTOR
            else:
                print("Max retries reached, skipping this batch.")
                return None


all_data = []


while True:
    print(f"Fetching batch with OFFSET {OFFSET}...")
    data = fetch_movies_in_batches(OFFSET)
    
    if data is None:
        print(f"Skipping batch with OFFSET {OFFSET} due to repeated errors.")
        OFFSET += BATCH_SIZE
        continue
    
    # Extract and store results
    results = data.get("results", {}).get("bindings", [])
    print(f"Data recieved : {len(results)}")
    if not results:
        print("No more results, ending pagination.")
        break
    
    # Process and store each result
    for result in results:
        if result["freebase_id"]["value"] == '/m/03vyhn':
            print(f'found {result["itemLabel"]["value"]}')
        movie = {
            "item": result["item"]["value"],
            "itemLabel": result["itemLabel"]["value"] if "itemLabel" in result else None,
            "imdb_id": result["imdb_id"]["value"] if "imdb_id" in result else None,
            "freebase_id": result["freebase_id"]["value"] if "freebase_id" in result else None,
            "budget": result["budget"]["value"] if "budget" in result else None,
            "award_received": result["award_received"]["value"] if "award_received" in result else None,
            "award_receivedLabel": result["award_receivedLabel"]["value"] if "award_receivedLabel" in result else None,
            "nominated_for": result["nominated_for"]["value"] if "nominated_for" in result else None,
            "nominated_forLabel": result["nominated_forLabel"]["value"] if "nominated_forLabel" in result else None
        }
        all_data.append(movie)
    
    # Increment OFFSET for the next batch
    OFFSET += BATCH_SIZE
    
    time.sleep(1)

df = pd.DataFrame(all_data)
df.to_csv("movies_with_awards.csv", index=False)