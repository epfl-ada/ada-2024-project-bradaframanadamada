import pandas as pd
import os

if __name__=='__main__':
    # load file containing characters and their personas
    assigned_clusters = pd.read_pickle('../data/processed_data0-9000.pkl')

    # load characters metadata
    character_data = pd.read_csv('../../data/character.metadata.tsv', sep='\t', index_col=0,
                                 names=['freebase_id', 'movie_release_date', 'character_name', 'actor_date_of_birth',
                                        'actor_gender', 'actor_height', 'actor_ethnicity', 'actor_name', 'actor_age',
                                        'freebase_char/actor_map', 'freebase_char_id', 'freebase_actor_id'])

    # set indices for inner join
    assigned_clusters.set_index(['wikipedia_id', 'name'], inplace=True)
    character_data.set_index([character_data.index, 'character_name'], inplace=True)
    character_data.index.names = ['wikipedia_id', 'name']

    # inner join on chracter name and movie id to link the personas to the actor who played them
    joined_df = assigned_clusters.join(character_data, how='inner')

    # sort by actor age at movie release
    # group by actor name
    # select attributes where an aggregate is needed
    # make a list of with these attributes for each group
    # result is a set of attributes, sorted chronologically, for each movies the actor played in
    # => actor career path
    newindex_df = joined_df.reset_index()
    result_df = newindex_df.sort_values(['actor_age'], ascending=True).groupby('actor_name')[['persona', 'actor_age', 'wikipedia_id']].agg(
        lambda x: list(x))

    # add the freebase actor id to each actor career path
    final_df = result_df.merge(joined_df[['freebase_actor_id', 'actor_name']], left_index=True, right_on='actor_name',
                    how='left').set_index('actor_name').drop_duplicates(subset=['freebase_actor_id'], keep='first')

    # rename columns to add clarity
    final_df.columns = ['personas_list', 'actor_age_during_movies', 'wikipedia_movies_id', 'freebase_actor_id']

    # save and print results
    final_df.to_pickle('../data/careers_paths.pkl')
    print(final_df)


