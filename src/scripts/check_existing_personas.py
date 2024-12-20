import pandas as pd
GOOD_PERSONAS = {'the warrior', 'the child', 'the orphan', 'the creator', 'the caregiver', 'the mentor', 'the joker', 'the magician', 'the ruler', 'the rebel', 'the lover', 'the seducer'}

def check_personas(df):
    """
    check if the personas are part of the 12 personas we defined
    @param df: dataframe containing actor paths, need a 'personas_list' row
    @return: num_actors, good_actors, num_movies, good_movies, all_goods, set_personas
        with:
        num_actors: number of actors
        good_actors: number of actors that have at least 1 good persona for each movie they played
        num_character: total number of character (role played in a movie by an actor)
        good_character: number of character that have at least 1 good persona in their personas list
        all_goods: boolean, True if all personas in the dataframe are part of the 12 personas
        set_personas: set of all existing personas in the dataframe
    """
    set_personas = set()
    good_character = 0
    good_actors = 0
    num_actors = 0
    num_character = 0
    all_goods = True
    for index, row in df.iterrows():
        num_actors += 1
        actor_is_ok = True
        for l in row['personas_list']:
            at_least_1_good = False
            num_character+=1
            for p in l:
                if p in GOOD_PERSONAS:
                    at_least_1_good = True
                set_personas.add(p)
            if at_least_1_good:
                good_character += 1
            else:
                all_goods = False
                actor_is_ok = False
        if actor_is_ok:
            good_actors += 1
    return num_actors, good_actors, num_character, good_character, all_goods, set_personas