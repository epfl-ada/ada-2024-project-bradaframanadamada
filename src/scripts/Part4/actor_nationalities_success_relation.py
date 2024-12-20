import pandas as pd
import ast
import plotly.graph_objects as go

from src.scripts.actors_normalized_popularity_scores import get_normalized_popularity_scores
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

def create_actor_nationalities_count_distribution():
    """
    This function creates an interactive bar chart to display the number of actor distribution by nationalities.
    """
    # Load the dataset that contains wikidata infos of the actors
    actors_wikidata = pd.read_csv("src/data/wikidata_actors_clean.csv", quotechar='"')
    # Only extract the actor name, the actor freebase ID and the nationalities columns from the data
    actors_wikidata = actors_wikidata[["actor_name", "freebase_id", "nationality_lst"]]
    # Transform the nationalities column into list
    actors_wikidata["nationality_lst"] = actors_wikidata["nationality_lst"].apply(
        lambda x: ast.literal_eval(x) if isinstance(x, str) else [])
    # Only keep the actors with a nationalities column present.
    actors_wikidata = actors_wikidata[actors_wikidata["nationality_lst"].apply(lambda x: len(x) > 0)]
    # explode the list of nationality of each actor
    actors_wikidata = actors_wikidata.explode("nationality_lst")
    # group the actors by nationalities
    actors_wikidata_nationality_group = actors_wikidata.groupby("nationality_lst")
    # count the number of actors per nationality group
    actor_nationality_count = actors_wikidata_nationality_group["freebase_id"].count().reset_index()
    actor_nationality_count.columns = ["Nationality", "Number of Actors"]

    # Sort the nationalities by the number of actors
    actor_nationality_count = actor_nationality_count.sort_values(by="Number of Actors", ascending=False)

    # Create an interactive bar chart with the Top 20 Nationalities with the most important number of actor.
    fig = px.bar(
        actor_nationality_count.head(20),
        x="Nationality",
        y="Number of Actors",
        text="Number of Actors",
        title="Top 20 Nationalities by Actor Count"
    )

    #  Add legends of the graph
    fig.update_layout(
        xaxis=dict(title="Nationality"),
        yaxis=dict(title="Actor Count"),
        height=600,  # such that the graph is entirely visible-
        showlegend=False,
        template="plotly_white",
    )
    # register the plot in html file
    fig.write_html("src/graphs/actors_nationalities_count_distribution.html")

    # Show the interactive bar chart
    fig.show()


def create_actor_nationalities_success_relation_graph(with_actor_count_weight):
    """
    This function creates a graph to visualize the relationship between actor nationalities and their popularity (calculated in
    function of the public's opinion on the actor (part 2 of the overall analysis, the awards that an actor received
    (Part 3 of the overall analysis), and the combination of the public's opinion and the awards received).

    `with_actor_count_weight`: Weighting factor for the actor count in each nationality. This value controls how much
    the number of actors count for each nationality group of actors influences the final success score. It is a float between 0 and 1:
        - A value of 0.0 means the actor count has no influence (score based uniquely on the mean of the popularity score of the actor).
        - A value of 1.0 means the actor count has full influence (score based entirely on actor count).
        - A value between 0.0 and 1.0 means the score is a weighted combination of the mean of the popularity score and the
        actor count per nationality category.
    """
    # Load the dataset that contains wikidata infos of the actors
    actors_wikidata = pd.read_csv("src/data/wikidata_actors_clean.csv", quotechar='"')
    # Only extract the actor name, the actor freebase ID and the nationalities columns from the data
    actors_wikidata = actors_wikidata[["actor_name", "freebase_id", "nationality_lst"]]
    # Transform the nationalities column into list
    actors_wikidata["nationality_lst"] = actors_wikidata["nationality_lst"].apply(lambda x: ast.literal_eval(x) if isinstance(x, str) else [])
    # Only keep the actors with a nationalities column present.
    actors_wikidata = actors_wikidata[actors_wikidata["nationality_lst"].apply(lambda x: len(x) > 0)]
    # Print the number of actors with their nationalities defined.
    print(f'Number of actors with a nationality list defined : {actors_wikidata.shape[0]}')

    # create a dataframe with normalised popularity scores
    popularity_scores = get_normalized_popularity_scores()

    # Merge the actors wikidata with the popularity scores
    actors_wikidata_with_popularity_scores = pd.merge(actors_wikidata,
                                                      popularity_scores,
                                                      how='inner',
                                                      left_on='freebase_id',
                                                      right_on='freebase_actor_id')

    # Only keep the relevant columns
    actors_wikidata_with_popularity_scores = actors_wikidata_with_popularity_scores[
        ["freebase_id","actor_name", "nationality_lst", "opinion_score", "award_score", "overall_score"]
    ]
    # Drop the row with nan
    actors_wikidata_with_popularity_scores = actors_wikidata_with_popularity_scores.dropna()
    # Print the number of actor with a university background, a success score (based on reviews and Box office) and an awards score defined
    print(f'Number of actors with a nationalities list, a success score (based on reviews and Box office) and an wards score defined : {actors_wikidata_with_popularity_scores.shape[0]}')

    # Establish the chance for an actor to become popular in function of his nationality
    # Group the data by the nationalities after having exploding the nationality list for each actor.
    nationalities_group = actors_wikidata_with_popularity_scores.explode("nationality_lst").groupby("nationality_lst")
    # for each member list of the nationality group calculate the mean of each popularity score and the total number of actor per nationality.
    nationality_stats = nationalities_group.agg(
        mean_opinion_score = ("opinion_score", "mean"),
        mean_award_score = ("award_score", "mean"),
        mean_overall_score = ("overall_score", "mean"),
        actor_count = ("freebase_id", "count")
    ).reset_index()

    # Normalize the actor count (from 0 to 1) to be able to realize a score that take into account both the mean popularity score and the actor count
    max_actor_count = nationality_stats["actor_count"].max()
    min_actor_count = nationality_stats["actor_count"].min()
    nationality_stats["normalized_actor_count"] = (nationality_stats["actor_count"] - min_actor_count) / (max_actor_count - min_actor_count)

    # calculate the score by take into account the average score of each nationality group and also the number of actors
    # per group. The weight of the actor count is given in function of the `weight`given in argument to the function.
    nationality_stats["weighted_mean_opinion_score"] = (
            nationality_stats["mean_opinion_score"] * (1 - with_actor_count_weight)
            + nationality_stats["normalized_actor_count"] * with_actor_count_weight
    )

    nationality_stats["weighted_mean_award_score"] = (
            nationality_stats["mean_award_score"] * (1 - with_actor_count_weight)
            + nationality_stats["normalized_actor_count"] * with_actor_count_weight
    )
    nationality_stats["weighted_mean_overall_score"] = (
            nationality_stats["mean_overall_score"] * (1 - with_actor_count_weight)
            + nationality_stats["normalized_actor_count"] * with_actor_count_weight
    )

    # Extract the top 20 nationalities for each score type
    sorted_opinion_score = nationality_stats.sort_values(by="weighted_mean_opinion_score", ascending=False).head(20)
    sorted_award_score = nationality_stats.sort_values(by="weighted_mean_award_score", ascending=False).head(20)
    sorted_overall_score = nationality_stats.sort_values(by="weighted_mean_overall_score", ascending=False).head(20)

    # Prepare data for plotting
    opinion_names = sorted_opinion_score["nationality_lst"].tolist()
    opinion_scores = sorted_opinion_score["weighted_mean_opinion_score"].tolist()

    award_names = sorted_award_score["nationality_lst"].tolist()
    award_scores = sorted_award_score["weighted_mean_award_score"].tolist()

    overall_names = sorted_overall_score["nationality_lst"].tolist()
    overall_scores = sorted_overall_score["weighted_mean_overall_score"].tolist()

    # Create an interactive bar chart
    fig = go.Figure()

    # add the trace for the opinion score
    fig.add_trace(go.Bar(
        x=opinion_scores,
        y=opinion_names,
        orientation='h',
        name='Opinion Score',
        marker_color='blue',
        hovertemplate=(
            '<b>Nationality: %{y}<br>'
            '<b>Wighted score: %{x}<br>'
            '<extra></extra>'
        ),
        visible=True
    ))

    # add the trace for the award score
    fig.add_trace(go.Bar(
        x=award_scores,
        y=award_names,
        orientation='h',
        name='Award Score',
        marker_color='red',
        hovertemplate=(
            '<b>Nationality: %{y}<br>'
            '<b>Wighted score: %{x}<br>'
            '<extra></extra>'
        ),
        visible=False
    ))

    # add the trace for the overall score
    fig.add_trace(go.Bar(
        x=overall_scores,
        y=overall_names,
        orientation='h',
        name='Overall Score',
        marker_color='green',
        hovertemplate=(
            '<b>Nationality: %{y}<br>'
            '<b>Wighted score: %{x}<br>'
            '<extra></extra>'
        ),
        visible=False
    ))

    # Dropdown menu for score selection
    fig.update_layout(
        updatemenus=[dict(
            type="dropdown",
            x=1,
            y=1.1,
            buttons=[
                dict(
                    label="Opinion Score",
                    method="update",
                    args=[{"visible": [True, False, False]}]  # Show only Opinion Score
                ),
                dict(
                    label="Award Score",
                    method="update",
                    args=[{"visible": [False, True, False]}]  # Show only Award Score
                ),
                dict(
                    label="Overall Score",
                    method="update",
                    args=[{"visible": [False, False, True]}]  # Show only Overall Score
                ),
            ]
        )],
        height=800,  # to be sure to see all the nationalities
        # add legends to the graph.
        title=f"Top 20 Nationalities with the most important Nationality Score with a weight of {with_actor_count_weight})",
        xaxis_title="Weighted score",
        yaxis_title="Nationality",
        template="plotly_white",
    )

    # register the plot in html file
    fig.write_html(f"src/graphs/actors_nationalities_popularity_relations_with_weight_{with_actor_count_weight}.html")

    # show the interactive graph
    fig.show()








