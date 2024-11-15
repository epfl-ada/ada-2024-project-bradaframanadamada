from src.data.some_dataloader import load_tsv
import ast
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

def load_and_preprocess_cmu(datapath):
    # We begin by loading the data
    movies_df = load_tsv(datapath + "movie.metadata.tsv")
    characters_df = load_tsv(datapath + "character.metadata.tsv")

    # We name the columns and pick which ones we want
    movies_df, characters_df = name_and_filter_columns(movies_df, characters_df)

    # We transform the movie genres and countries from a string dict to a list
    movies_df = refactor_movie_genres_countries(movies_df)

    # We refactor the release date (take only the year and cast to int)
    movies_df = refactor_movie_release_date(movies_df)

    # We do the same with the date of birth
    characters_df = refactor_actor_dob(characters_df)

    # We cast actor age to int
    characters_df['Actor age at movie release'] = characters_df['Actor age at movie release'].astype('Int64')

    # We join the two dataframes
    joined_df = characters_df.join(movies_df.set_index('Freebase movie ID'), on='Freebase movie ID', how='left')

    # We deduce the actor age at movie release from actor date of birth and movie release date and remove those two columns as well as the row where the age is still missing.
    joined_df = complete_age(joined_df)

    return joined_df



def name_and_filter_columns(movies_df, characters_df):
    """
    :param movies_df: The raw movies Dataframe
    :param characters_df: The raw characters Dataframe
    :return: (movies_df, characters_df)The Dataframe with columns renamed and filtered

    """

    movies_df.columns = ['Wikipedia movie ID', 'Freebase movie ID', 'Movie name', 'Movie release date', 'Movie box office revenue', 'Movie runtime', 'Movie languages', 'Movie countries', 'Movie genres']
    characters_df.columns = ['Wikipedia movie ID', 'Freebase movie ID', 'Movie release date', 'Character name', 'Actor date of birth', 'Actor gender', 'Actor height (in meters)', 'Actor ethnicity (Freebase ID)', 'Actor name', 'Actor age at movie release', 'Freebase character/actor map ID', 'Freebase character ID', 'Freebase actor ID']

    movies_df = movies_df[['Freebase movie ID', 'Movie name', 'Movie release date', 'Movie countries', 'Movie genres']]
    characters_df = characters_df[['Freebase movie ID', 'Character name', 'Actor date of birth', 'Actor gender', 'Actor name', 'Actor age at movie release', 'Freebase character ID', 'Freebase actor ID']]

    return movies_df, characters_df

def plot_nan_values(df, plot_title):
    plt.rcParams.update({'font.size': 10})
    plt.figure(figsize=(20, 6), dpi=80)

    plt.title(plot_title)

    print(f"Total entries: {len(df)}\n")
    print(df.isnull().sum())
    indices = df.isnull().sum().index.to_list()
    nan_count = df.isnull().sum().to_list()
    plt.bar(indices, nan_count)

def print_nan_info(df):
    """
    Print the nan in each column of the two Dataframes

    :param df: The Dataframe
    """

    print(f"Total entries: {len(df)}\n")
    print(df.isnull().sum())

def refactor_movie_genres_countries(movies_df):
    """
    Take the genres and countries column, transform the string dictionary into a list and return

    :param movies_df: The movies Dataframe
    :return: The refactored movies Dataframe
    """
    movies_df['Movie genres'] = movies_df['Movie genres'].apply(lambda s: list(ast.literal_eval(s).values()))
    movies_df['Movie countries'] = movies_df['Movie countries'].apply(lambda s: list(ast.literal_eval(s).values()))
    return movies_df

def refactor_movie_release_date(movies_df):
    """
    Take the movies Dataframe, select the release date, take only the year, do a bounds check and return the refactored Dataframe

    :param movies_df: The movies Dataframe
    :return: refactored Dataframe
    """
    movies_df['Movie release date'] = movies_df['Movie release date'].apply(
        lambda complete_date: str(complete_date)[:4] if complete_date is not np.nan and 1800 < int(
            complete_date[:4]) < 2050 else None).astype('Int64')
    return movies_df

def refactor_actor_dob(characters_df):
    """
    Take the characters Dataframe, select the date of birth, take only the year, do a bounds check and return the refactored Dataframe

    :param characters_df: The characters Dataframe
    :return: refactored Dataframe
    """
    characters_df['Actor date of birth'] = characters_df['Actor date of birth'].apply(
        lambda complete_date: str(complete_date)[:4] if complete_date is not np.nan and 1800 < int(
            complete_date[:4]) < 2050 else None).astype('Int64')
    return characters_df

def complete_age(df):
    """
    Add values in the 'Actor age at movie release' column by subtracting the 'Movie release date' column by he 'Actor date birth' column, drop the rows where 'Actor age at movie release' is NaN and remove 'Actor date of birth' and 'Movie release date' columns.

    :param df: The Dataframe
    :return: Completed and cleaned Dataframe
    """
    indices = np.where(pd.isna(df['Actor age at movie release']))[0]
    df.loc[indices, 'Actor age at movie release'] = df.loc[indices, 'Movie release date'] - df.loc[indices, 'Actor date of birth']
    df = df.drop(columns=['Actor date of birth', 'Movie release date'])

    return df