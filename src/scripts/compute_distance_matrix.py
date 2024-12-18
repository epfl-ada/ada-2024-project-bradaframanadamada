import pandas as pd
from tqdm import tqdm
import numpy as np

GOOD_PERSONAS = {'the warrior', 'the child', 'the orphan', 'the creator', 'the caregiver', 'the mentor','the joker', 'the magician', 'the ruler', 'the rebel', 'the lover', 'the seducer'}

def vecorize_personas(possibilities, list):
    """
    create a vector of size len(possibilities) encoding a list of personas
    @param possibilities: set of personas that will be dimensions of the encoding
    @param list: list of personas to encode
    @return: list with 1 for each possibility contained in the list and 0 otherwise
    """
    return [1 if persona in list else 0 for persona in possibilities]

def vecorize_personas_list(possibilities, list):
    """
    vectorize each element of a list of list of personas
    @param possibilities: set of personas that will be dimensions of the encoding
    @param list: list of lists of personas to encode
    @return: vectorized representation of each element of list
    """
    return [vecorize_personas(possibilities, sublist) for sublist in list]

def sum_vectorized_personas(vectorized_personas):
    """
    compute vectorized representation of a career by summing the vectorized representation of each movie
    @param vectorized_personas: numpy array of shape (num_movies, num_good_personas), containing representation of each movie
    @return: numpy array of shape (1, num_good_personas), sum along axis 0 of vectorized_personas
    """
    return np.sum(vectorized_personas, axis=0)

def create_distance_matrix(summed_personas):
    """
    compute L1 distance matrix for each career paths in summed_personas
    @param summed_personas: numpy array of shape (num_actors, num_good_personas), containing representation of each actor career path
    @return: numpy array of shape (num_actors, num_actors), distance matrix
    """
    m = np.zeros((len(summed_personas), len(summed_personas)))
    for i, persona1 in tqdm(enumerate(summed_personas)):
        for j, persona2 in enumerate(summed_personas):
            similarity = np.sum(np.abs(persona1-persona2))
            m[i, j] = similarity
    return m

if __name__ == '__main__':
    df = pd.read_pickle('../data/clean_careers_paths.pkl')
    df['vectorized_personas'] = (df['personas_list'].apply(lambda personas_list: np.array(vecorize_personas_list(GOOD_PERSONAS, personas_list))))
    df['summed_personas'] = df['vectorized_personas'].apply(sum_vectorized_personas)
    matrix = create_distance_matrix(df['summed_personas'])
    np.savetxt('../data/distance_matrix.txt', matrix, delimiter=',')