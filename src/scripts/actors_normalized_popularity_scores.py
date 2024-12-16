import pandas as pd

def get_normalized_popularity_scores():
    """This function add columns to the given dataframe with the normalised opinion and award scores,
    and calculated a new score based both on the award score and on the opinion score.
    """
    # Load the dataset that contains the success score based on the film's review and the box office.
    actors_success = pd.read_csv("src/data/actors_success.csv")
    # rename the column opinion_score
    actors_success = actors_success.rename(columns={"score": "opinion_score"})

    # Load the dataset that contains the success score based on the actor's awards.
    actors_awards = pd.read_csv("src/data/actors_awards_scores.csv")
    # rename the column score
    actors_awards = actors_awards.rename(columns={"score": "award_score"})

    # merge the two popularity scores.
    merge_scores = pd.merge(actors_success,
                  actors_awards,
                  how="inner",
                  left_on="freebase_actor_id",
                  right_on="freebase_actor_id")

    print(f'Number of actors with both opinion and award popularity scores: {merge_scores.shape[0]}')

    # Normalize the score on percent
    max_opinion_score = merge_scores['opinion_score'].max()
    min_opinion_score = merge_scores['opinion_score'].min()
    merge_scores["opinion_score"] = (merge_scores["opinion_score"] - min_opinion_score) / (max_opinion_score - min_opinion_score)

    max_award_score = merge_scores['award_score'].max()
    min_award_score = merge_scores['award_score'].min()
    merge_scores["award_score"] = (merge_scores["award_score"] - min_award_score) / (max_award_score - min_award_score)

    # add a new score that equally take into account the score (based on the reviews and Box office) and the score based on the award)
    merge_scores["overall_score"] = merge_scores.apply(lambda x: (x["opinion_score"] + x["award_score"]) * 0.5, axis=1)

    return merge_scores