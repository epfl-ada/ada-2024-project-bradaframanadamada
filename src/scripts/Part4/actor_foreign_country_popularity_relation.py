import pandas as pd
import plotly.graph_objects as go
import ast
from src.scripts.actors_normalized_popularity_scores import get_normalized_popularity_scores

def count_number_of_actors_who_played_in_their_country():
    """
    This function calculates and visualizes the number of actors who have played in countries corresponding to their nationality.
    """
    # load the CMU data
    cmu_df = pd.read_pickle("src/data/metadata_cmu.pkl")
    # load the actor wikidata
    actor_wikidata = pd.read_csv("src/data/wikidata_actors_clean.csv", quotechar='"')

    # combine the actor's wikidata with the CMU dataframe.
    join_actor_wikidata_CMU = cmu_df.merge(actor_wikidata, left_on='Freebase actor ID', right_on='freebase_id', how='inner')
    # convert nationality and movie country string to list
    join_actor_wikidata_CMU['nationality_lst'] = join_actor_wikidata_CMU['nationality_lst'].apply( lambda x: ast.literal_eval(x) if pd.notna(x) else [])
    # add a field in the dataframe to know if the actor has currently played in a country of his nationality
    join_actor_wikidata_CMU['correlation production country nationality'] = join_actor_wikidata_CMU.apply(
        lambda x: len(set(x['nationality_lst']).intersection(x['Movie countries'])) >= 1, axis=1)

    # Count occurrences of True and False in the correlation
    correlation_counts = join_actor_wikidata_CMU['correlation production country nationality'].value_counts()

    # visualize the results
    # Create an interactive bar plot using Plotly
    fig = go.Figure(data=[
        go.Bar(
            x=['No', 'Yes'],
            y=correlation_counts.values,
            marker=dict(color=['red', 'green']),
            text=correlation_counts.values,
            textposition='auto'
        )
    ])

    # Customize the layout
    fig.update_layout(
        title="Actors Who Played in a Country of Their Nationality",
        xaxis_title="Correlation",
        yaxis_title="Number of Actors",
        template="plotly_white",
        showlegend=False
    )

    # register the plot in html file
    fig.write_html(f"src/graphs/actors_count_who_played_in_their_country.html")

    # Show the interactive plot
    fig.show()

def actors_performance_own_foreign_country_performance_distribution(with_actor_count_weight):
    """
    This function creates a graph to visualize the relationship between the country where the actors have perfomed
    (distinction of own country nationality + foreign country) and their popularity (calculated in function of the public's
    opinion on the actor (part 2 of the overall analysis, the awards that an actor received (Part 3 of the overall analysis),
    and the combination of the public's opinion and the awards received).

    `with_actor_count_weight`: Weighting factor for the actor count in each performed country (own country + foreign country lis).
    This value controls how much the number of actors count for each nationality group of actors influences the final success score.
    It is a float between 0 and 1:
        - A value of 0.0 means the actor count has no influence (score based uniquely on the mean of the popularity score of the actor).
        - A value of 1.0 means the actor count has full influence (score based entirely on actor count).
        - A value between 0.0 and 1.0 means the score is a weighted combination of the mean of the popularity score and the
        actor count per performance's country category.
    """
    # load the CMU data
    cmu_df = pd.read_pickle("src/data/metadata_cmu.pkl")
    # load the actor wikidata
    actor_wikidata = pd.read_csv("src/data/wikidata_actors_clean.csv", quotechar='"')

    # combine the actor's wikidata with the CMU dataframe.
    join_actor_wikidata_CMU = cmu_df.merge(actor_wikidata, left_on='Freebase actor ID', right_on='freebase_id', how='inner')
    # convert nationality and movie country string to list
    join_actor_wikidata_CMU['nationality_lst'] = join_actor_wikidata_CMU['nationality_lst'].apply( lambda x: ast.literal_eval(x) if pd.notna(x) else [])
    own_country_label = "Own Country"
    # add a field in the dataframe to know if the actor has currently played in a country of his nationality
    join_actor_wikidata_CMU['performance_country'] = join_actor_wikidata_CMU.apply(
        lambda x: [
            own_country_label if movie_country in x['nationality_lst'] else movie_country
            for movie_country in x['Movie countries']
        ], axis=1
    )
    # retrive the diffrent succes score
    success_score = get_normalized_popularity_scores()

    # add the scores
    join_actor_wikidata_CMU = pd.merge(
        join_actor_wikidata_CMU,
        success_score,
        how='inner',
        left_on='Freebase actor ID',
        right_on='freebase_actor_id'
    )
    # Establish the chance for an actor to become popular in function of his performance country (own country or other foreign country)
    # Group the data by the nationalities after having exploding the nationality list for each actor.
    country_group = join_actor_wikidata_CMU.explode("performance_country").groupby("performance_country")
    # for each member list of the nationality group calculate the mean of each popularity score and the total number of actor per nationality.
    country_stats = country_group.agg(
        mean_opinion_score=("opinion_score", "mean"),
        mean_award_score=("award_score", "mean"),
        mean_overall_score=("overall_score", "mean"),
        actor_count=("freebase_id", "count")
    ).reset_index()

    # Normalize the actor count (from 0 to 1) to be able to realize a score that take into account both the mean popularity score and the actor count
    max_actor_count = country_stats["actor_count"].max()
    min_actor_count = country_stats["actor_count"].min()
    country_stats["normalized_actor_count"] = (country_stats["actor_count"] - min_actor_count) / (
                max_actor_count - min_actor_count)

    # calculate the score by take into account the average score of each nationality group and also the number of actors
    # per group. The weight of the actor count is given in function of the `weight`given in argument to the function.
    country_stats["weighted_mean_opinion_score"] = (
            country_stats["mean_opinion_score"] * (1 - with_actor_count_weight)
            + country_stats["normalized_actor_count"] * with_actor_count_weight
    )

    country_stats["weighted_mean_award_score"] = (
            country_stats["mean_award_score"] * (1 - with_actor_count_weight)
            + country_stats["normalized_actor_count"] * with_actor_count_weight
    )
    country_stats["weighted_mean_overall_score"] = (
            country_stats["mean_overall_score"] * (1 - with_actor_count_weight)
            + country_stats["normalized_actor_count"] * with_actor_count_weight
    )

    # Extract the top 20 universities for each score type
    sorted_opinion_score = country_stats.sort_values(by="weighted_mean_opinion_score", ascending=False).head(20)
    sorted_award_score = country_stats.sort_values(by="weighted_mean_award_score", ascending=False).head(20)
    sorted_overall_score = country_stats.sort_values(by="weighted_mean_overall_score", ascending=False).head(20)

    # Prepare data for plotting
    opinion_names = sorted_opinion_score["performance_country"].tolist()
    opinion_scores = sorted_opinion_score["weighted_mean_opinion_score"].tolist()

    award_names = sorted_award_score["performance_country"].tolist()
    award_scores = sorted_award_score["weighted_mean_award_score"].tolist()

    overall_names = sorted_overall_score["performance_country"].tolist()
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
            '<b>Country: %{y}<br>'
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
            '<b>Country: %{y}<br>'
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
            '<b>Country: %{y}<br>'
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
        title=f"Top 20 Country to perform in with the most important Popularity Score with a weight of {with_actor_count_weight})",
        xaxis_title="Weighted score",
        yaxis_title="Country",
        template="plotly_white",
    )


    # register the plot in html file
    fig.write_html(f"src/graphs/actors_performance_own_foreign_country_performance_distribution.html")

    # Show the interactive plot
    fig.show()

