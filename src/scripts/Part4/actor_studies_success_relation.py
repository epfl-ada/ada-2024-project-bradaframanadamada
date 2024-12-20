from collections import Counter
import pandas as pd
import ast
import plotly.express as px
import plotly.graph_objects as go
from src.scripts.actors_normalized_popularity_scores import get_normalized_popularity_scores
import numpy as np

def create_actor_studies_actor_count_distribution():
    """
    This function constructs an interactive bar chart to show the distribution of the number of actors across
    universities, displaying the top 20 universities with the highest number of actor attendees.
    """
    # load the actor wikidata
    actor_wikidata = pd.read_csv("src/data/wikidata_actors_clean.csv", quotechar='"')
    # flatten the list of all universities present on each actor row
    universities_lst = [university for actorUniversityLst in actor_wikidata['alma_mater_lst'].apply(ast.literal_eval) for
                       university in set(actorUniversityLst)]  # make each university unique for each actor

    # count the occurrence of each university
    university_count = Counter(universities_lst)

    # visualize the results
    df_university_count = pd.DataFrame(university_count.items(), columns=['university_name', 'number_of_actors'])
    # sort the results and select only the top 20
    df_university_count = df_university_count.sort_values(by=['number_of_actors'], ascending=False).head(20)

    #Create an interactive bar chart
    fig = px.bar(df_university_count,
                 x='number_of_actors',
                 y='university_name',
                 orientation='h',
                 title='Top 20 Universities with the Most Actor Attendees',
                 labels={'number_of_actors': 'Number of Actors', 'university_name': 'University Name'},
                 height=800, # to see all the universities
                 template='plotly_white')

    # Save the graph into html file
    fig.write_html("src/graphs/actors_universities_count_distribution.html")

    # Show the plot
    fig.show()

def create_actor_studies_success_relation_graph(with_actor_count_weight):
    """
    This function creates a graph to visualize the relationship between actor universities study and their popularity (calculated in
    function of the public's opinion on the actor (part 2 of the overall analysis, the awards that an actor received
    (Part 3 of the overall analysis), and the combination of the public's opinion and the awards received).

    `with_actor_count_weight`: Weighting factor for the actor count in each nationality. This value controls how much
    the number of actors count for each nationality group of actors influences the final success score. It is a float between 0 and 1:
        - A value of 0.0 means the actor count has no influence (score based uniquely on the mean of the popularity score of the actor).
        - A value of 1.0 means the actor count has full influence (score based entirely on count of the actors who studied in a given university).
        - A value between 0.0 and 1.0 means the score is a weighted combination of the mean of the popularity score and the
        actor count per university category.
    """
    # load the dataset that contains wikidata infos of the actors
    actors_wikidata = pd.read_csv("src/data/wikidata_actors_clean.csv", quotechar='"')
    # only extract the actor name, the actor freebase ID and the alma_mater (universities background) from the data
    actors_wikidata = actors_wikidata[["actor_name", "freebase_id", "alma_mater_lst"]]
    # Transform the alma_matter column into list
    actors_wikidata["alma_mater_lst"] = actors_wikidata["alma_mater_lst"].apply(lambda x: ast.literal_eval(x) if isinstance(x, str) else [])
    # Only keep the actors with a university background present.
    actors_wikidata = actors_wikidata[actors_wikidata["alma_mater_lst"].apply(lambda x: len(x) > 0)]
    # Print the number of actors with a university background defined.
    print(f'Number of actors with a university background defined : {actors_wikidata.shape[0]}')
    
    # load the success score
    success_score = get_normalized_popularity_scores()

    # retrieve the score of the actor
    actors_wikidata = pd.merge(actors_wikidata,
                              success_score,
                              how='inner',
                              left_on='freebase_id',
                              right_on='freebase_actor_id')

    # Only keep the relevant columns
    actors_wikidata = actors_wikidata[
        ["freebase_id","actor_name", "alma_mater_lst", "opinion_score", "award_score", "overall_score"]
    ]
    # drop the row with nan
    actors_wikidata = actors_wikidata.dropna()
    # Print the number of actor with a university background, a success score (based on reviews and Box office) and an awards score defined
    print(f'Number of actors with a university background, a success score (based on reviews and Box office) and an awards score defined : {actors_wikidata.shape[0]}')

    # Establish the chance for an actor to become popular in function of his university
    # Group the data by the universities after having exploding the alma_matter list for each actor.
    university_group = actors_wikidata.explode("alma_mater_lst").groupby("alma_mater_lst")



    # for each member list of the university group calculate the mean of each popularity score and the total number of actor per university.
    university_stats = university_group.agg(
        mean_opinion_score=("opinion_score", "mean"),
        mean_award_score=("award_score", "mean"),
        mean_overall_score=("overall_score", "mean"),
        actor_count=("freebase_id", "count")
    ).reset_index()
    # Normalized the actor count with max-min normalization.
    max_actor_count = university_stats["actor_count"].max()
    min_actor_count = university_stats["actor_count"].min()
    university_stats["normalized_actor_count"] = (
            (university_stats["actor_count"] - min_actor_count) / (max_actor_count - min_actor_count)
    )

    # calculate the score by take into account the average score of each university group and also the number of actors
    # per group. The weight of the actor count is given in function of the `weight`given in argument to the function.
    university_stats["weighted_mean_opinion_score"] = (
            university_stats["mean_opinion_score"] * (1 - with_actor_count_weight)
            + university_stats["normalized_actor_count"] * with_actor_count_weight
    )
    university_stats["weighted_mean_award_score"] = (
            university_stats["mean_award_score"] * (1 - with_actor_count_weight)
            + university_stats["normalized_actor_count"] * with_actor_count_weight
    )
    university_stats["weighted_mean_overall_score"] = (
            university_stats["mean_overall_score"] * (1 - with_actor_count_weight)
            + university_stats["normalized_actor_count"] * with_actor_count_weight
    )

    # Extract the top 20 universities for each score type
    sorted_opinion_score = university_stats.sort_values(by="weighted_mean_opinion_score", ascending=False).head(20)
    sorted_award_score = university_stats.sort_values(by="weighted_mean_award_score", ascending=False).head(20)
    sorted_overall_score = university_stats.sort_values(by="weighted_mean_overall_score", ascending=False).head(20)

    # Prepare data for plotting
    opinion_names = sorted_opinion_score["alma_mater_lst"].tolist()
    opinion_scores = sorted_opinion_score["weighted_mean_opinion_score"].tolist()

    award_names = sorted_award_score["alma_mater_lst"].tolist()
    award_scores = sorted_award_score["weighted_mean_award_score"].tolist()

    overall_names = sorted_overall_score["alma_mater_lst"].tolist()
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
            '<b>University name: %{y}<br>'
            '<b>University score: %{x}<br>'
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
            '<b>University name: %{y}<br>'
            '<b>University score: %{x}<br>'
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
            '<b>University name: %{y}<br>' 
            '<b>University score: %{x}<br>'
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
        height = 800,  # to see all the universities
        # add legends to the graph.
        title = f"Top 20 Universities with the most important University Score with a weight of {with_actor_count_weight})",
        xaxis_title = "Score",
        yaxis_title = "University",
        template = "plotly_white",
    )

    # register the plot in html file
    fig.write_html(f"src/graphs/actors_universities_popularity_relations_with_weight_{with_actor_count_weight}.html")

    # show the interactive graph
    fig.show()