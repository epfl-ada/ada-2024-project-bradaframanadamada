import pandas as pd
import ast
import matplotlib.pyplot as plt

def create_actor_studies_success_relation_graph():
    # load the dataset that contains wikidata infos of the actors
    actors_wikidata = pd.read_csv("src/data/wikidata_actors_clean.csv")
    # only extract the actor name, the actor freebase ID and the alma_mater (universities background) from the data
    actors_wikidata = actors_wikidata[["actor_name", "freebase_id", "alma_mater_lst"]]
    # Transform the alma_matter column into list
    actors_wikidata["alma_mater_lst"] = actors_wikidata["alma_mater_lst"].apply(lambda x: ast.literal_eval(x) if isinstance(x, str) else [])
    # Only keep the actors with a university background present.
    actors_wikidata = actors_wikidata[actors_wikidata["alma_mater_lst"].apply(lambda x: len(x) > 0)]
    # Print the number of actors with a university background defined.
    print(f'Number of actors with a university background defined : {actors_wikidata.shape[0]}')
    # Load the dataset that contains the success score based on the film's review and the box office.
    actors_success = pd.read_csv("src/data/actors_success.csv")
    # Join the actors with a university background with the success score.
    actors_wikidata_with_success = pd.merge(actors_wikidata,
                                            actors_success,
                                            how="left",
                                            left_on="freebase_id",
                                            right_on="freebase_actor_id")
    # Only keep the relevant columns
    # rename the column opinion_score
    actors_wikidata_with_success = actors_wikidata_with_success.rename(columns={"score": "opinion_score"})
    actors_wikidata_with_success = actors_wikidata_with_success[["freebase_id","actor_name", "alma_mater_lst", "opinion_score"]]
    # Print the number of actor who have both a university background and a success score defined.
    print(f'Number of actors with a university background and a success score (based on reviews and box office) defined : {actors_wikidata_with_success.shape[0]}')
    # Load the dataset that contains the success score based on the actor's awards.
    actors_awards = pd.read_csv("src/data/actors_awards_scores.csv")
    # rename the column score
    actors_awards = actors_awards.rename(columns={"score": "award_score"})
    # Join the actors with a university background and a success score (based on reviews and box office) with the actor's award score.
    actors_wikidata_with_award_success_and_awards = pd.merge(actors_wikidata_with_success,
                                                             actors_awards,
                                                             how="left",
                                                             left_on="freebase_id",
                                                             right_on="freebase_actor_id")
    # Only keep the relevant columns
    actors_wikidata_with_award_success_and_awards = actors_wikidata_with_award_success_and_awards[
        ["freebase_id","actor_name", "alma_mater_lst", "opinion_score", "award_score"]
    ]
    # drop the row with nan
    actors_wikidata_with_award_success_and_awards = actors_wikidata_with_award_success_and_awards.dropna()
    # Print the number of actor with a university background, a success score (based on reviews and Box office) and an awards score defined
    print(f'Number of actors with a university background, a success score (based on reviews and Box office) and an wards score defined : {actors_wikidata_with_award_success_and_awards.shape[0]}')

    # Normalize the score on percent
    max_opinion_score = actors_wikidata_with_award_success_and_awards['opinion_score'].max()
    min_opinion_score = actors_wikidata_with_award_success_and_awards['opinion_score'].min()
    actors_wikidata_with_award_success_and_awards["opinion_score"] = (
            (actors_wikidata_with_award_success_and_awards["opinion_score"] - min_opinion_score)/(max_opinion_score - min_opinion_score))

    max_award_score = actors_wikidata_with_award_success_and_awards['award_score'].max()
    min_award_score = actors_wikidata_with_award_success_and_awards['award_score'].min()
    actors_wikidata_with_award_success_and_awards["award_score"] = (
        (actors_wikidata_with_award_success_and_awards["award_score"] - min_award_score)/(max_award_score - min_award_score))

    # add a new score that equally take into account the score (based on the reviews and Boy office) and the score based on the award)
    actors_wikidata_with_award_success_and_awards["overall_score"] = actors_wikidata_with_award_success_and_awards.apply(lambda x: (x["opinion_score"] + x["award_score"]) * 0.5, axis=1)

    # establish a score of the universities based on the opinion, award and overall actor's scores.
    university_scores = {}
    for _, row in actors_wikidata_with_award_success_and_awards.iterrows():
        for university in row["alma_mater_lst"]:
            if university not in university_scores:
                university_scores[university] = {
                    'opinion_score': 0,
                    'award_score': 0,
                    'overall_score': 0
                }
            else:
                university_scores[university]['opinion_score'] += row['opinion_score']
                university_scores[university]['award_score'] += row['award_score']
                university_scores[university]['overall_score'] += row['overall_score']

    # Normalize the scores
    max_university_opinion_score = max([university['opinion_score'] for university in university_scores.values()])
    min_university_opinion_score = min([university['opinion_score'] for university in university_scores.values()])

    max_university_award_score = max([university['award_score'] for university in university_scores.values()])
    min_university_award_score = min([university['award_score'] for university in university_scores.values()])

    max_university_overall_score = max([university['overall_score'] for university in university_scores.values()])
    min_university_overall_score = min([university['overall_score'] for university in university_scores.values()])

    for university in university_scores.keys():
        university_scores[university]['opinion_score'] = (university_scores[university]['opinion_score'] - min_university_opinion_score) / (max_university_opinion_score - min_university_opinion_score)
        university_scores[university]['award_score'] = (university_scores[university]['award_score'] - min_university_award_score) / (max_university_award_score - min_university_award_score)
        university_scores[university]['overall_score'] = (university_scores[university]['opinion_score'] - min_university_overall_score) / (max_university_overall_score - min_university_overall_score)

    # Extract the top 20 universities for each score type
    sorted_opinion_score = sorted(university_scores.items(), key=lambda x: x[1]['opinion_score'], reverse=True)[:20]
    sorted_award_score = sorted(university_scores.items(), key=lambda x: x[1]['award_score'], reverse=True)[:20]
    sorted_overall_score = sorted(university_scores.items(), key=lambda x: x[1]['overall_score'], reverse=True)[:20]

    # Prepare data for plotting
    opinion_names = [university[0] for university in sorted_opinion_score]
    opinion_scores = [university[1]['opinion_score'] for university in sorted_opinion_score]

    award_names = [university[0] for university in sorted_award_score]
    award_scores = [university[1]['award_score'] for university in sorted_award_score]

    overall_names = [university[0] for university in sorted_overall_score]
    overall_scores = [university[1]['overall_score'] for university in sorted_overall_score]

    # Create subplots
    fig, axes = plt.subplots(2, 2, figsize=(20, 20))

    # Plot for Opinion Scores
    axes[0][0].barh(opinion_names, opinion_scores, color='blue')
    axes[0][0].set_title("Top 20 Universities by Opinion Score")
    axes[0][0].set_xlabel("Opinion Score")
    # Display the bars horizontally
    axes[0][0].invert_yaxis()

    # Plot for Award Scores
    axes[0][1].barh(award_names, award_scores, color='red')
    axes[0][1].set_title("Top 20 Universities by Award Score")
    axes[0][1].set_xlabel("Award Score")
    axes[0][1].invert_yaxis()

    # Plot for Overall Scores
    axes[1][0].barh(overall_names, overall_scores, color='green')
    axes[1][0].set_title("Top 20 Universities by Overall Score")
    axes[1][0].set_xlabel("Overall Score")
    axes[1][0].invert_yaxis()

    # Adjust the layouts to evict graph overlapping.
    plt.tight_layout()

    plt.show()


    return pd.DataFrame.from_dict(university_scores)