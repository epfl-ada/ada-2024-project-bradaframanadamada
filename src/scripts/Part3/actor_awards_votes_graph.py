import pandas as pd
import plotly.express as px

from src.scripts.actors_normalized_popularity_scores import get_normalized_popularity_scores


def create_actor_awards_votes_graphs():
    """
       This function creates an interactive scatter plot displaying actor popularity based on awards and votes.
       """
    max_size = 30;
    min_size = 4;
    data = get_normalized_popularity_scores()
    data['award_score'] = data['award_score'].fillna(0)
    data["z_score_opinion"] = (data["opinion_score"] - data["opinion_score"].mean()) / \
                                      data["opinion_score"].std()
    data["z_score_award"] = (data["award_score"] - data["award_score"].mean()) / data[
        "award_score"].std()
    data["z_score_overall"] = (data["overall_score"] - data["overall_score"].mean()) / \
                                      data["overall_score"].std()
    data["scaled_size"] = 2*( (data["overall_score"] - data[
                                                     "overall_score"].min())
                                                 / (data["overall_score"].max() - data[
                                             "overall_score"].min())
                                                 * (max_size - min_size)
                                         ) + min_size
    #data.head(5000)
    data = data.rename(columns={"scaled_size": "Size",
                                "award_score": "Prestige Score",
                                "overall_score": "Overall Score",
                                "opinion_score": "Public Opinion Score",
                                "z_score_award": "Average Awards Deviation",
                                "z_score_overall": "Overall Deviation",
                                "z_score_opinion": "Average Opinion Deviation",
                                "name": "Actor Awards Votes",})

    fig = px.scatter(
        data,
        x='Prestige Score',
        y='Public Opinion Score',
        color = 'Overall Deviation',
        size = 'Size',
        color_continuous_scale=px.colors.sequential.ice_r,
        hover_name="Actor",
        hover_data={"Prestige Score": True,
                    "Public Opinion Score": True,
                    "Overall Score": True,
                    "Average Awards Deviation": True,
                    "Average Opinion Deviation": True,
                    "Overall Deviation": True,
                    "Size": False,
        },
        template="plotly_white",
    )
    fig.update_traces(marker=dict(line=dict(width=0))) #I dont want to see the contours
    fig.show()

    # Save graph to an HTML file
    #fig.write_html("src/graphs/actor_awards_votes_graphs.html")