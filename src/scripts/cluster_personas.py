import pandas as pd
from openai import OpenAI
import os
from pydantic import BaseModel

#=================================================#
# define format type for a character-personas tuple
class CharacterPersona(BaseModel):
    name: str
    persona: list[str]

# define gpt output format as a list of character-personas tuple
class AllCharacters(BaseModel):
    characters: list[CharacterPersona]

#=================================================#
def load_data(path='data/plot_summaries.txt'):
    """
    load the summaries txt file as dataframe
    @param path: path to txt file
    @return: the data as a dataframe, with the wikipedia id as index and a summary column
    """
    return pd.read_table(path, index_col=None, names=['summary'], sep='\t')

def extract_persona(summary: str, api_key):
    """
    use openai API to extract characters and their personas from summary
    use the gpt4o mini model
    @param summary: movie summary as a string
    @param api_key: openai api key
    @return: the completion object resulting from the query
    """
    tasks = [{'role':'user', 'content':summary}]
    client = OpenAI(api_key=api_key)
    completion = client.beta.chat.completions.parse(
        model='gpt-4o-mini',
        messages=[
            {'role':'system', 'content':'given a movie summary, you will extract the characters and their personas. Your answers should respect the given structure'},
            {'role':'assistant', 'content':'the possible personas are: the warrior, the child, the orphan, the creator, the caregiver, the mentor, the joker, the magician, the ruler, the rebel, the lover, the seducer'}
        ]+tasks,
        response_format=AllCharacters,
    )
    return completion

def compute_one_movie(summary, api_key):
    """
    extract characters and their personas from summary
    @param summary: summary of a movie as a string
    @param api_key: openai api key
    @return: a dataframe with 2 columns containing the characters and their personas
    """
    completion = extract_persona(summary, api_key)
    df = pd.DataFrame(i.model_dump() for s in completion.choices[0].message.parsed for i in s[1])
    return df

def compute_subset(start, end, api_key, datapath='data/plot_summaries.txt', result_folder='src/data'):
    """
    extract characters and their personas for movies in [start,end)
    and save the resulting dataframe as pickle
    @param start: start index of interval
    @param end: end index of interval
    @param api_key: openai api key
    @param datapath: path to summaries txt file
    @param result_folder: path where extraction results will be saved
    @return: a dataframe with 3 columns containing:
            the characters, their personas and the wikipedia movie id
    """
    dfs = []
    data = load_data(datapath).reset_index(names='wikipedia_id')
    for i in range(start, end):
        summary = data.iloc[i]['summary']
        df = compute_one_movie(i, summary, api_key)
        df['wikipedia_id'] = data.iloc[i]['wikipedia_id']
        dfs.append(df)
    processed_data = pd.concat(dfs)
    processed_data.to_pickle(result_folder + f'/processed_data{start}-{end}.pkl')
    return processed_data

#=================================================#
if __name__ == '__main__':
    # manually select this
    # (limit should be around 10000 requests per day
    # calling it on the full data might crash)
    start = 0
    end = 2
    #=========================================#
    api_key = os.environ['OPENAI_API_KEY']
    comp = compute_subset(start, end, api_key, datapath='data/plot_summaries.txt')
    print(comp)


