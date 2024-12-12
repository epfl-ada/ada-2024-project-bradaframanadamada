# ada-2024-project-bradaframanadamada

# Presentation

# Defining Success in Acting: Analysing Career Paths, Role Choices, and Film Impact

## Abstract

The goal of our analysis is to understand the factors that define a successful actor's career, focusing on career paths, role choices, and the film in which the actor chooses to appear. We will first try to find the possible career path of an actor and the different stages of his career according to the character type and the role of this character that an actor has played and the genre he has played in. We will then try to understand which actor's career/ career path is successful by analysing the budgets of the films where the actor has played in and the opinion of the spectator on a film.  We will study the awards that a film or an actor obtains in different categories or world regions to analyse the impact of an actor in the cinematographic community. Finally, we will study if the academic part, the family or the nationality of an actor can play a role in the success of an actor's career. 

## Research questions
### Main research question: 

**What characteristics make an actor’s career successful ?**

### Some sub questions we aim to answer:

1. **What are the possible career paths, steps and possible trajectories ? (Q1)**

2. **How can we define a good actor's performance based on the film’s success he performed in ? (Q2)**

3. **How can we measure the impact of an award on an actor's career in the cinematic field ? (Q3)**

4. **Does the academic and environmental background of an actor have an impact on his career success ? (Q4)**

## Proposed additional datasets
- **Wikidata:** It is used for films to extract the imdb id, budget, awards, nomination based on the freebase ID of the films in the CMU dataset. We have extracted all wikidata information from the freebase actor ID:  the birth date, death date, the gender, the actor’s imdb_id, the nationality list, the occupation list, the spouse list, the children list, the academic background, the list of awards received. We also extracted wikidata information from the character freebase ID: the occupation list, the allies of the characters, the wikidata ID and the actor’s affiliation list. 

- **IMDB:** this dataset is used to get the audience ratings of a film which will be used along the budget and box office revenue.

- **AWARDS:** This dataset (https://github.com/DLu/oscar_data) is used to get which movies and actors are nominees for the awards and in which category

## Methods
### For Q1: 
**Character’s archetype extraction:** We will use the NLP model GPT4o mini to extract each character from the film’s summary and assign to each character their archetypes. The clusters on the character’s archetype are defined using the classification defined on this website (see: https://nofilmschool.com/character-archetypes). We have also extracted for each actor wikidata their occupation (actor, singer, ...) which can give more information. There is also the character’s occupation defined in the wikidata character but we are not sure if we will use this data since not a lot of character’s have wikidata information, we can use it to complete the character type analysis obtained previously. 

**Defined actor’s career step and paths:** We will identify some stages through the career of an actor. We will look at how many films have been made in a given period. We will also see which genre is the prefered during a certain stage of the actor's career or if he/she changed their favorite realisation country. 

**Movie genre selection by the actor:** We will study if an actor always plays in the same genre of film or if he plays in a large number of films.

### For Q2:
**Wikidata extraction:** Use the sparql api to extract all the film related data from wikidata.

**Preprocessing and cleaning:** Link the wikidata, cmu and imdb ratings dataset and clean it.

**Analyse the data:** Analyse the resulting dataset and try to see for correlation between the budget, ratings and box office to answer the Q2.

### For Q3:
**Preprocessing and cleaning:** Clean and analyse separately the awards coming from the wikidata actor database and the Award database.

**Link the data and analyse:** Link the two dataset and analyse the data obtained to answer to the Q3.

### For Q4:
**Impact of the family environment:** By extracting from the wikidata of actors the children and the spouses and by using the actor’s success from Q2 and Q3, we will try to understand if the family environment has an influence on his career’s success. 

**Impact of the academic background:**  By extracting the academic background from the actor wikidata, we will see if given universities have formed many notorious actors(notoriety extracted from Q2 and Q3). 

**Impact of the actor’s nationality:** We can study the relation between the film's country production and the nationality of the actor, and also the relation between the actor’s nationality and the actor’s notoriety ( from Q2 and Q3). 

## Proposed timeline
- **From 28/10 to 03/11:** Project brainstorming
- **From 04/11 to 10/11:** Write the project structure with main questions and subquestions part.
- **From  11/11 to 17/11:** Write the report of the milestone 2, extract the wikidata, do first processing to extract character archetype with the NLP model, MMLU date cleaning and processing. Present the first results. 
- **From 18/11 to 01/12:** Data processing of each of the sub questions separately + Homework 2. 
- **From 02/12 to 08/12:** Link the different sub questions to be able to understand the question of each part.
- **From 09/12 to 15/12:** Do the structure of the website + create the first visualisation of the data.
- **From 16/12 to 22/12:** Finalise the website and complete with explanation to answer clearly to the sub questions and the main problem, and the conclusion (possible opening: recommender for the career actor choices). 

## Organisation within the team
- **(Q1) Personas and roles in the film** (Hof & Fleury)
- **(Q1) Age Period and career stage** (Beuret)
- **(Q2) Film success** (Kurmann)
- **(Q3) Award** (Steiner)
- **(Q4) Family, academic and nationality impact** (Hof and maybe  others)

## Questions for TAs (optional)
Idea on the possible visualisation of the different career paths ?



## Project Structure

The directory structure of the project looks like this:

```
├── data                        <- Project data files
│
├── src                         <- Source code
│   ├── data                            <- Data directory
│   ├── models                          <- Model directory
│   ├── utils                           <- Utility directory
│   ├── scripts                         <- Shell scripts
│
├── tests                       <- Tests of any kind
│
├── results.ipynb               <- a well-structured notebook showing the results
│
├── .gitignore                  <- List of files ignored by git
├── pip_requirements.txt        <- File for installing python dependencies
└── README.md
```
[Click here to open the main website](data_stories.html)