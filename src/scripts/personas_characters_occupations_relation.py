from collections import Counter

import pandas as pd
import ast
import plotly.graph_objects as go

def create_relation_graph_personas_characters_occupations():
    """
        This function creates an interactive bar chart that shows the relationship between personas and their associated characters occupations.
    """

    # Load the careers paths of the actors to retrieve the list of their personas.
    personas_dataset = pd.read_pickle('src/data/clean_careers_paths_good_personas.pkl')
    # Only keep the relevant infos
    personas_dataset =  personas_dataset[['personas_list', 'wikipedia_movies_id', 'freebase_actor_id']]

    # Load the dataset that contains the activities of each character.
    character_dataset = pd.read_csv('src/data/wikidata_characters_clean.csv')
    # Only keep the relevant infos
    character_dataset = character_dataset[['freebase_id', 'occupation_lst']]

    # Load the dataset that contains the cmu movies infos
    cmu_data = pd.read_pickle("src/data/metadata_cmu.pkl")
    # Only keep the relevant information from the CMU data
    cmu_data = cmu_data[['Wikipedia movie ID', 'Freebase actor ID', 'Freebase character ID']]
    # remove the duplicates
    cmu_data = cmu_data.drop_duplicates(subset=['Wikipedia movie ID', 'Freebase actor ID', 'Freebase character ID'])

    # Explode the lists of personas dataset to have a single list of personas associated to a single wikidata id.
    df_personas_wikidata_id = personas_dataset.explode(['personas_list','wikipedia_movies_id'])
    print(f'Number of tuples (wikipedia_movie_id, freebase_actor_id) associated to a list of personas: {df_personas_wikidata_id.shape[0]}')

    # merge the obtain dataset with teh cmu_data to retrieve the character freebase id for each tuple (wikipedia movie id, freebase actor id)
    df_personas_wikidata_id_characters = pd.merge(
        df_personas_wikidata_id,
        cmu_data,
        how='inner',
        left_on=['wikipedia_movies_id', 'freebase_actor_id'],
        right_on=['Wikipedia movie ID', 'Freebase actor ID']
    )
    print(f'Number of tuples (wikipedia_movie_id, freebase_actor_id) associated to a list of personas and a character freebase id: {df_personas_wikidata_id.shape[0]}')

    # only select from the wikidata character database actor with an occupation.
    character_dataset['occupation_lst'] = character_dataset['occupation_lst'].dropna().apply(lambda x: ast.literal_eval(x))
    characters_with_occupation = character_dataset[character_dataset['occupation_lst'].apply(lambda x: isinstance(x, list) and len(x) > 0)]
    print(f'Number of characters with occupation: {characters_with_occupation.shape[0]}')

    # associated each personas list to the corresponding character's occupations
    df_personas_wikidata_id_characters_occupations = pd.merge(
        df_personas_wikidata_id_characters,
        characters_with_occupation,
        how='inner',
        left_on='Freebase character ID',
        right_on='freebase_id'
    )

    print(f'Number of characters with a list of personas and an occupation list : {df_personas_wikidata_id_characters_occupations.shape[0]}')
    print(f'Since a character is present more than one time in the role distribution, each character can be associated to more than one list of personas.')

    # only associate each persona list to a list of character's occupations
    df_personas_occupations = df_personas_wikidata_id_characters_occupations[['personas_list', 'occupation_lst']]

    # Explode the list of personas.
    df_personas_occupations = df_personas_occupations.explode('personas_list')

    # Explode the list of occupations
    df_personas_occupations = df_personas_occupations.explode('occupation_lst')

    # count how many times time each tuple is present
    personas_occupation_count = Counter(zip(df_personas_occupations['personas_list'], df_personas_occupations['occupation_lst']))

    # Create a structure to be able to plot the data
    personas_characters_occupations_plot_data = {}
    for (persona, occupation), count in personas_occupation_count.items():
        if persona not in personas_characters_occupations_plot_data:
            personas_characters_occupations_plot_data[persona] = {}
        personas_characters_occupations_plot_data[persona][occupation] = count

    # Create a list of personas for dropdown
    personas = list(personas_characters_occupations_plot_data.keys())

    # Create the interactive bar chart plot.
    fig = go.Figure()

    # Create a bar plot graph for each persona
    for persona in personas:
        occupation_counts = personas_characters_occupations_plot_data[persona]
        # retrieve the first 20 most important character's occupations
        top_occupations = sorted(occupation_counts.items(), key=lambda x: x[1], reverse=True)[:20]
        occupations = [occupation for occupation, _ in top_occupations]
        counts = [count for _, count in top_occupations]

        # Add the data for each persona in a separate sub bar plot.
        fig.add_trace(go.Bar(
            x=occupations,
            y=counts,
            name=persona,
            hovertemplate='Occupation: %{x}<br>Count: %{y}',
            # When the mouse is over the bar, display additional infos.
            text=occupations,  # Add the occupation name as hover text
            visible=False,  # Initially make all traces invisible
        ))

    # Set the first persona bar chart graph visible.
    fig.data[0].visible = True

    # Create the dropdown menu for persona selection
    dropdown_personas_selection = [
        {
            'label': persona,
            'method': 'update',
            'args': [
                {'visible': [persona == selected_persona for selected_persona in personas]},
                # Update teh graph with the selected persona.
                {'title': f'Top 20 Character\'s occupations in relation with the {persona}\'s persona.'},
            ]
        } for persona in personas
    ]

    # Update the layout with dropdown to select a persona
    fig.update_layout(
        title=f'Top 20 Character\'s occupations in relation with the {personas[0]}\'s persona.',
        xaxis_title='Occupations',
        yaxis_title='Count',
        xaxis_tickangle=-45,
        hovermode='closest',
        height=800,
        updatemenus=[
            {
                'buttons': dropdown_personas_selection,
                'direction': 'down',
                'showactive': True,
                'active': 0,
                'x': 0.5,
                'xanchor': 'left',
                'y': 1.15,
                'yanchor': 'top',
            }
        ]
    )
    # save the interactive graph in the graphs folder
    fig.write_html("src/graphs/personas_characters_occupations_relations_graph_interactive.html")
    # Show the interactive graph
    fig.show()