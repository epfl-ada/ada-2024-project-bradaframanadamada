import pandas as pd
GOOD_PERSONAS = {'the warrior', 'the child', 'the orphan', 'the creator', 'the caregiver', 'the mentor',
                     'the joker', 'the magician', 'the ruler', 'the rebel', 'the lover', 'the seducer'}

def contains_at_least_k_good_personas(personas_list, k):
    """
    check if a list of personas contains at least k personas that are part of the 12 personas
    @param personas_list: list of personas as strings
    @param k: threshold of 'good' personas
    @return: True if the list contains at least k personas that are part of the 12 personas, False otherwise
    """
    num_good = 0
    for persona in personas_list:
        if persona in GOOD_PERSONAS:
            num_good += 1
    return num_good >= k

def is_unproblematic_actor(career):
    """
    check if an actor have at least 1 good persona for each movie he played in.
    @param career: list of list of personas as strings
    @return: True if the list contains at least 1 good persona for each movie, False otherwise
    """
    unproblematic = True
    for movie in career:
        is_ok = contains_at_least_k_good_personas(movie, 1)
        if not is_ok:
            unproblematic = False
    return unproblematic

def filter_out_problematic_actors(careers_path):
    """
    filter out rows that are problematic if we drop 'bad' personas
    @param careers_path: dataframe with a 'personas_list' column representing the careers path personas
    @return: dataframe with only the rows that contain at least 1 good persona for each movie
    """
    careers = careers_path['personas_list']
    unproblematics = careers.apply(is_unproblematic_actor)
    return careers_path[unproblematics.values]

def drop_bad_personas_in_movie(personas_list):
    """
    make sure all personas are part the 12 good personas
    @param personas_list: list of personas as strings
    @return: list of personas that are in the 12 good personas list, dropping the rest
    """
    good_list = []
    for persona in personas_list:
        if persona in GOOD_PERSONAS:
            good_list.append(persona)
    return good_list

def drop_bad_personas_in_path(career):
    """
    drop bad personas for all movies in the career
    @param career: list of list of personas as strings
    @return: list of list of personas that are in the 12 good personas list, dropping the rest
    """
    return [drop_bad_personas_in_movie(movie) for movie in career]

def drop_bad_personas(careers_path):
    """
    drop personas that are not part of the 12 good personas
    @param careers_path: dataframe with a 'personas_list' column representing the careers path personas
    @return: dataframe with 'personas_list' column containing only personas from the 12 good personas
    """
    good_personas =  careers_path['personas_list'].apply(drop_bad_personas_in_path)
    careers_path['personas_list'] = good_personas
    return careers_path

if __name__ == '__main__':
    # read datafram with all sort of personas
    df = pd.read_pickle('../data/clean_careers_paths.pkl')
    # drop all rows that would results in empty lists
    df = filter_out_problematic_actors(df)
    # drop all personas that are not in the 12 personas defined
    df = drop_bad_personas(df)
    print(df)
    df.to_pickle('../data/clean_careers_paths_good_personas.pkl')
