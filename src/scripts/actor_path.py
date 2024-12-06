import pandas as pd
import os

if __name__=='__main__':
    # load file containing characters and their personas
    assigned_clusters = pd.read_pickle('../data/processed_data.pkl')

    # load characters metadata
    character_data = pd.read_pickle('../data/metadata_cmu.pkl')

    # set indices for inner join
    assigned_clusters.set_index(['wikipedia_id', 'name'], inplace=True)
    character_data.set_index(['Wikipedia movie ID', 'Character name'], inplace=True)
    character_data.index.names = ['wikipedia_id', 'name']
    print(assigned_clusters.columns)
    print(character_data.columns)

    # inner join on character name and movie id to link the personas to the actor who played them
    joined_df = assigned_clusters.join(character_data, how='inner')

    # sort by actor age at movie release
    # group by actor name
    # select attributes where an aggregate is needed
    # make a list of with these attributes for each group
    # result is a set of attributes, sorted chronologically, for each movie the actor played in
    # => actor career path
    newindex_df = joined_df.reset_index()
    result_df = newindex_df.sort_values(['Actor age at movie release'], ascending=True).groupby('Actor name')[['persona', 'Actor age at movie release', 'wikipedia_id']].agg(
        lambda x: list(x))

    # add the freebase actor id to each actor career path
    final_df = result_df.merge(joined_df[['Freebase actor ID', 'Actor name']], left_index=True, right_on='Actor name',
                    how='left').set_index('Actor name').drop_duplicates(subset=['Freebase actor ID'], keep='first')

    # rename columns to add clarity
    final_df.columns = ['personas_list', 'actor_age_during_movies', 'wikipedia_movies_id', 'freebase_actor_id']

    # save and print results
    final_df.to_pickle('../data/clean_careers_paths.pkl')
    print(final_df)


