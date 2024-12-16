import pandas as pd
import ast
from matplotlib import pyplot as plt
from src.scripts.actors_normalized_popularity_scores import get_normalized_popularity_scores

def create_actor_nationalities_success_relation_graph():
    """
    This function creates a graph to visualize the relationship between actor nationalities and their popularity (calculated in
    function of the public's opinion on the actor (part 2 of the overall analysis, the awards that an actor received
    (Part 3 of the overall analysis), and the combination of the public's opinion and the awards received).
    """
    # Load the dataset that contains wikidata infos of the actors
    actors_wikidata = pd.read_csv("src/data/wikidata_actors_clean.csv")
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

    # Print the stats fpr the 10 first nationalities who have the best overall popularity score.
    print("Statistics of 10 Nationalities with the best mean overall popularity score:")
    print(nationality_stats.sort_values(by="mean_overall_score", ascending=False).head(10))

    # Normalize the actor count (from o to 1) to be able to realize a score that take into account both the mean popularity score and the actor count
    max_actor_count = nationality_stats["actor_count"].max()
    min_actor_count = nationality_stats["actor_count"].min()
    nationality_stats["normalized_actor_count"] = (nationality_stats["actor_count"] - min_actor_count) / (max_actor_count - min_actor_count)

    # Create teh weighted score that take both the mean popularises score and the number of actor by nationalities
    nationality_stats["weighted_mean_opinion_score"] = 0.5 * nationality_stats["mean_opinion_score"] + 0.5 * nationality_stats["normalized_actor_count"]
    nationality_stats["weighted_mean_award_score"] = 0.5 * nationality_stats["mean_award_score"] + 0.5 * nationality_stats["normalized_actor_count"]
    nationality_stats["weighted_mean_overall_score"] = 0.5 * nationality_stats["mean_overall_score"] + 0.5 * nationality_stats["normalized_actor_count"]

    # Print the stats for the 10 first nationalities who have the best overall popularity score.
    print("Statistics of 10 Nationalities with the best weighted mean overall popularity score:")
    print(nationality_stats.sort_values(by="weighted_mean_overall_score", ascending=False).head(10))

    # Extract the top 20 nationalities for each score type
    sorted_opinion_score = nationality_stats.sort_values(by="weighted_mean_opinion_score", ascending=False)
    sorted_award_score = nationality_stats.sort_values(by="weighted_mean_award_score", ascending=False)
    sorted_overall_score = nationality_stats.sort_values(by="weighted_mean_overall_score", ascending=False)

    # Prepare data for plotting
    opinion_names = [row["nationality_lst"] for _, row in sorted_opinion_score.iterrows()][:20]
    opinion_scores = [row["weighted_mean_opinion_score"] for _, row in sorted_opinion_score.iterrows()][:20]

    award_names = [row["nationality_lst"] for _, row in sorted_award_score.iterrows()][:20]
    award_scores = [row["weighted_mean_award_score"] for _, row in sorted_opinion_score.iterrows()][:20]

    overall_names = [row["nationality_lst"] for _, row in sorted_overall_score.iterrows()][:20]
    overall_scores = [row["weighted_mean_overall_score"] for _, row in sorted_opinion_score.iterrows()][:20]

    # Create subplots
    fig, axes = plt.subplots(2, 2, figsize=(20, 20))

    # Plot for Opinion Scores
    axes[0][0].barh(opinion_names, opinion_scores, color='blue')
    axes[0][0].set_title("Top 20 Nationalities by Opinion Score")
    axes[0][0].set_xlabel("Opinion Score")
    # Display the bars horizontally
    axes[0][0].invert_yaxis()

    # Plot for Award Scores
    axes[0][1].barh(award_names, award_scores, color='red')
    axes[0][1].set_title("Top 20 Nationalities by Award Score")
    axes[0][1].set_xlabel("Award Score")
    axes[0][1].invert_yaxis()

    # Plot for Overall Scores
    axes[1][0].barh(overall_names, overall_scores, color='green')
    axes[1][0].set_title("Top 20 Nationalities by Overall Score")
    axes[1][0].set_xlabel("Overall Score")
    axes[1][0].invert_yaxis()

    # Adjust the layouts to evict graph overlapping.
    plt.tight_layout()

    plt.show()

    return nationality_stats
