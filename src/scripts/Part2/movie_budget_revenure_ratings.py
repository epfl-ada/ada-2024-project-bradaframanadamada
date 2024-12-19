import pandas as pd
import plotly.express as px


def create_movie_budget_revenue_ratings_graph():
    """
        This function creates an interactive scatter plot that displays the movies where the actors have played in.
    """

    # load all dataset
    films = pd.read_csv('src/data/movie_wikidata_cmu_imdb_clean_box_office.csv')

    films.dropna(subset=['numVotes'], inplace=True)
    films = films.fillna('Not Available')
    films = films[['name', 'release_date', 'box_office', 'budget', 'averageRating', 'numVotes']]
    films.columns = ['Movie', 'Release Date', 'Box Office (USD)', 'Budget (USD)', 'Average Ratings',
                        'Number of Votes']

    fig = px.scatter(
        films,
        x='Budget (USD)',
        y='Box Office (USD)',
        size='Number of Votes',
        color='Average Ratings',
        hover_name="Movie",
        hover_data={
            "Release Date": True,
            "Average Ratings": True,
            "Number of Votes": True,
            "Budget (USD)": True,
            "Box Office (USD)": True, },
        title='Performance of films based on budget, box office, ratings and number of votes',
    )

    # Save graph to an HTML file
    # fig.write_html("src/graphs/movies_budget_revenue_ratings_graph.html")

    fig.show()