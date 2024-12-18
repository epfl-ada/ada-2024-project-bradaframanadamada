import pandas as pd
import ast
from src.utils.retrieve_parents_from_children import ParentsFromChildrenRetriever
import plotly.graph_objects as go
from src.scripts.actors_normalized_popularity_scores import get_normalized_popularity_scores

def create_graph_actors_with_spouses_actor_distribution():
    """
    Creates an interactive bar chart showing the distribution of actors based on the number of their spouses
    who are also actors.
    """
    # load the actor's wikidata
    actor_wikidata = pd.read_csv("src/data/wikidata_actors_clean.csv")

    # transform the string of the columns of spouses into array.
    actor_wikidata['spouse_lst'] = actor_wikidata['spouse_lst'].apply(ast.literal_eval)

    # calculate for each actor the number of spouses which is also an actor
    actor_wikidata['number_spouse_also_actor'] = actor_wikidata['spouse_lst'].apply(
        lambda spouseLst: sum(1 for elem in spouseLst if elem in actor_wikidata['actor_name'].values))

    number_of_spouses = actor_wikidata['number_spouse_also_actor'].value_counts().sort_index()

    print(f'Value count of the number of spouses who are also actor: {number_of_spouses}')

    # only take into account the actor with at least one spouse in the visualization.
    number_of_spouses = number_of_spouses[number_of_spouses.index > 0]

    # create the interactive bar chart
    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=number_of_spouses.index,
        y=number_of_spouses.values,
        marker_color='blue',
        text=number_of_spouses.values,
        hovertemplate='<b>Number of Actor spouses:  %{x}<br>'+
        '<b>Number of Actors:  %{y}<extra></extra>',
    ))
    # add legends to the graph
    fig.update_layout(
        title='Distribution of the number of spouses (who are also actors) for each actor',
        xaxis_title='Number of spouses who are also actors',
        yaxis_title='Number of Actors',
        xaxis=dict(tickmode='linear'),  # Ensure all ticks appear
        template='plotly_white'
    )

    # Save the graph in a html file
    fig.write_html("src/graphs/actors_spouses_number_distribution.html")

    # Show the graph
    fig.show()

def create_graph_actors_with_spouses_popularity_correlation():
    """
        This function used the actor wikidata and actor popularity score to analyze the correlation between actor popularity
        and the popularity of their spouses.
    """
    # load the actor's wikidata
    actor_wikidata = pd.read_csv("src/data/wikidata_actors_clean.csv")
    actor_wikidata_orig = pd.read_csv("src/data/wikidata_actors_clean.csv")

    # transform the string of the columns of spouses into array.
    actor_wikidata['spouse_lst'] = actor_wikidata['spouse_lst'].apply(ast.literal_eval)

    # explode the spouses list
    actor_wikidata = actor_wikidata.explode('spouse_lst')

    # ony keep the row with non-empty spouse column
    actor_wikidata = actor_wikidata[actor_wikidata['spouse_lst'].notnull()]

    # only keep the relevant infos
    actor_wikidata = actor_wikidata[['freebase_id', 'actor_name', 'spouse_lst']]

    # retrieve the freebase  id of the spouses
    actor_wikidata = pd.merge(actor_wikidata,
                              actor_wikidata_orig[['freebase_id', 'actor_name']],
                              how='inner',
                              left_on='spouse_lst',
                              right_on='actor_name',
                              )
    actor_wikidata = actor_wikidata.rename(columns={'freebase_id_x': 'freebase_id',
                                                    'actor_name_x': 'actor_name',
                                                    'spouse_lst': 'spouse',
                                                    'freebase_id_y': 'spouse_freebase_id'})
    actor_wikidata = actor_wikidata[['freebase_id', 'actor_name', 'spouse', 'spouse_freebase_id']]

    # load the different actor's popularity score
    actors_popularity_score = get_normalized_popularity_scores()

    # retrieve the score of the actor
    actor_wikidata = pd.merge(actor_wikidata,
                              actors_popularity_score,
                              how='inner',
                              left_on='freebase_id',
                              right_on='freebase_actor_id')
    actor_wikidata = actor_wikidata.rename(columns={'overall_score': 'overall_score_actor',
                                                    'opinion_score': 'opinion_score_actor',
                                                    'award_score': 'award_score_actor'})
    actor_wikidata = actor_wikidata[['freebase_id', 'actor_name', 'spouse', 'spouse_freebase_id', 'opinion_score_actor',
                                     'award_score_actor', 'overall_score_actor']]

    # retrieve the score of the spouses
    actor_wikidata = pd.merge(actor_wikidata,
                              actors_popularity_score,
                              how='inner',
                              left_on='spouse_freebase_id',
                              right_on='freebase_actor_id')
    actor_wikidata = actor_wikidata.rename(columns={'overall_score': 'overall_score_spouse',
                                                    'opinion_score': 'opinion_score_spouse',
                                                    'award_score': 'award_score_spouse'})
    actor_wikidata = actor_wikidata[
        ['freebase_id', 'actor_name', 'spouse', 'spouse_freebase_id', 'opinion_score_actor', 'award_score_actor',
         'overall_score_actor', 'opinion_score_spouse', 'award_score_spouse', 'overall_score_spouse']]

    # Drop the row with NA values
    actor_wikidata = actor_wikidata.dropna()

    # Now calculate the Pearson correlation ti show if there is a correlation between the scores
    correlation_opinion_score = actor_wikidata[['opinion_score_actor', 'opinion_score_spouse']].corr().iloc[0, 1]
    correlation_award_score = actor_wikidata[['award_score_actor', 'award_score_spouse']].corr().iloc[0, 1]
    correlation_overall_score = actor_wikidata[['overall_score_actor', 'overall_score_spouse']].corr().iloc[0, 1]

    # Print the correlation results
    print(f"Correlation between Actor and Spouse Opinion Scores: {correlation_opinion_score:.3f}")
    print(f"Correlation between Actor and Spouse Award Scores: {correlation_award_score:.3f}")
    print(f"Correlation between Actor and Spouse Overall Scores: {correlation_overall_score:.3f}")

    # Visualize the results in graph that present the contrast between the actor popularity score and the spouses popularity score.
    fig = go.Figure()

    # Add a trace for the opinion score
    fig.add_trace(go.Scatter(
        x=actor_wikidata['opinion_score_spouse'],
        y=actor_wikidata['opinion_score_actor'],
        mode='markers',
        name='Opinion Score',
        marker_color='blue',
        text=actor_wikidata['actor_name'],
        customdata=actor_wikidata['spouse'],
        hovertemplate=(
            '<b>Actor: %{text} with score: %{x}<br>'  # Actor name and score
            '<b>Spouse: %{customdata} with score: %{y}<br>'  # spouse name and score
            '<extra></extra>'
        ),
        visible=True  # The first graph displayed.
    ))
    # Add a trace for the award score
    fig.add_trace(go.Scatter(
        x=actor_wikidata['award_score_spouse'],
        y=actor_wikidata['award_score_actor'],
        mode='markers',
        name='Award Score',
        marker_color='red',
        text=actor_wikidata['actor_name'],
        customdata=actor_wikidata['spouse'],
        hovertemplate=(
            '<b>Actor: %{text} with score: %{x}<br>'  # Actor name and score
            '<b>Spouse: %{customdata} with score: %{y}<br>'  # Spouse name and score
            '<extra></extra>'
        ),
        visible=False
    ))
    # Add a trace for the overall score
    fig.add_trace(go.Scatter(
        x=actor_wikidata['overall_score_spouse'],
        y=actor_wikidata['overall_score_actor'],
        mode='markers',
        name='Overall Score',
        marker_color='red',
        text=actor_wikidata['actor_name'],
        customdata=actor_wikidata['spouse'],
        hovertemplate=(
            '<b>Actor: %{text} with score: %{x}<br>'  # Actor name and score
            '<b>Spouse: %{customdata} with score: %{y}<br>'  # Spouse name and score
            '<extra></extra>'
        ),
        visible=False
    ))

    # Update layout with title and axis labels
    fig.update_layout(
        title="Actor Popularity score in comparison to the his Spouse popularity score.",
        xaxis_title="Spouse Popularity Score",
        yaxis_title="Actor Popularity Score",
        template="plotly_white",
        showlegend=True,
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
        )]
    )
    # register the plot in html file
    fig.write_html("src/graphs/actors_spouses_popularity_correlation.html")

    # Show the plot
    fig.show()