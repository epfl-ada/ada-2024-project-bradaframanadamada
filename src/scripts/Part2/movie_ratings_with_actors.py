import pandas as pd
import plotly.express as px


def create_movie_ratings_with_actors_graph():
    """
        This function creates an interactive scatter plot that displays the movies where the actors have played in.
    """

    # load all dataset
    actors = pd.read_csv('src/data/character.metadata.tsv', sep='\t',
                         names=['useless', 'freebase_movie_id', 'movie_release_date', 'character_name', 'date_of_birth',
                                'gender', 'height', 'ethnicity', 'name', 'actor age', 'useless2', 'useless3',
                                'freebase_actor_id'])

    films = pd.read_csv('src/data/movie_wikidata_cmu_imdb_clean_box_office.csv')

    actor_votes = pd.read_csv('src/data/actors_success.csv')

    # Merge datasets on freebase_movie_id
    movies_with_actors = pd.merge(actors, films, left_on="freebase_movie_id", right_on="freebase_id",
                                  how="outer").dropna(
        subset=['averageRating', 'numVotes', 'release_date', 'name_y', 'name_x'])
    movies_with_actors = movies_with_actors[
        ['freebase_actor_id', 'name_x', 'freebase_id', 'name_y', 'release_date', 'box_office', 'budget',
         'averageRating', 'numVotes']]
    movies_with_actors.columns = ['freebase_actor_id', 'Actor', 'freebase_movie_id', 'Movie', 'Release Date',
                                  'Box Office (USD)', 'Budget (USD)', 'Average Ratings', 'Number of Votes']

    ratings_graph_data = movies_with_actors[
        movies_with_actors['freebase_actor_id'].isin(actor_votes.head(250)['freebase_actor_id'])].sort_values(
        by='Actor')
    ratings_graph_data = ratings_graph_data.fillna('Not Available')

    # Generate the interactive graph
    fig = px.scatter(
        ratings_graph_data,
        x="Release Date",
        y="Average Ratings",
        size="Number of Votes",
        size_max=50,
        color="Actor",
        hover_name="Movie",
        hover_data={"Actor": False,
                    "Release Date": True,
                    "Average Ratings": True,
                    "Number of Votes": True,
                    "Budget (USD)": True,
                    "Box Office (USD)": True, },
        title="Number of Votes vs. Average Rating by Movie"
    )

    # only display the top 5 actor by default
    i = 0
    top5index = ratings_graph_data.drop_duplicates(subset='freebase_actor_id', keep='first').reset_index()
    top5index = top5index[top5index['freebase_actor_id']
        .isin(actor_votes.head(5)['freebase_actor_id'])].index.tolist()

    for scat in fig.data:
        if i not in top5index:
            scat.visible = "legendonly"
        i+= 1

    # Save graph to an HTML file
    # fig.write_html("src/graphs/actor_movies_rating_graph.html")

    fig.show()