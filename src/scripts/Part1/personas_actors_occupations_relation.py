import pandas as pd
import ast
from collections import Counter
import plotly.graph_objects as go

def create_relation_graph_personas_occupations():
    """
        This function creates an interactive bar chart that shows the relationship for an actor between personas and their associated occupations.
    """
    # Load the careers paths of the actors to retrieve the list of their personas.
    personas_dataset = pd.read_pickle('src/data/clean_careers_paths_good_personas.pkl')
    # Load the dataset that contains the activities of each actor.
    actor_dataset = pd.read_csv('src/data/wikidata_actors_clean.csv', quotechar='"')

    # Merge the two dataset with their freebase actor ID
    actor_merged = pd.merge(personas_dataset,
                            actor_dataset,
                            how='inner',
                            left_on='freebase_actor_id',
                            right_on='freebase_id')

    # Check how many relation we have
    print(f'Initial number of actor with personas : {personas_dataset.shape[0]}. \n'
          f'Initial number of actors with occupations : {actor_dataset.shape[0]}. \n'
          f'Number of actors with occupations and personas: {actor_merged.shape[0]}. \n')

    # Extract the relations between the actor's personas and occupations.
    personas_occupations_pairs = []
    # Iterate over all the lines of the dataset.
    for _, row in actor_merged.iterrows():
        # Check if 'occupation' is not NaN
        if pd.notna(row['occupation_lst']):
            # Transform the list in string format into a real list (due to the fact that the data are registered in a CSV file).
            occupations = ast.literal_eval(row['occupation_lst'])
            # Concatenate the personas
            personas = set([elem for sub_lst in row['personas_list'] for elem in sub_lst])
            # Iterate over all the personas
            for persona in personas:
                # Iterate over all the occupations
                    for occupation in occupations:
                        # remove all the occupations more relative to the actor since it is evident.
                        if occupation not in ['actor', 'film actor', 'television actor']:
                            personas_occupations_pairs.append((persona, occupation))

    # Count the number of occurrences of each pair
    personas_occupations_count = Counter(personas_occupations_pairs)

    # Create a structure to be able to plot the data
    personas_occupations_plot_data = {}
    for (persona, occupation), count in personas_occupations_count.items():
        if persona not in personas_occupations_plot_data:
            personas_occupations_plot_data[persona] = {}
        personas_occupations_plot_data[persona][occupation] = count

    # Create a list of personas for dropdown
    personas = list(personas_occupations_plot_data.keys())

    # Create the interactive bar chart plot.
    fig = go.Figure()

    # Create a bar plot graph for each persona
    for persona in personas:
        occupation_counts = personas_occupations_plot_data[persona]
        # retrieve the first 20 most important occupations
        top_occupations = sorted(occupation_counts.items(), key=lambda x: x[1], reverse=True)[:20]
        occupations = [occupation for occupation, _ in top_occupations]
        counts = [count for _, count in top_occupations]

        # Add the data for each persona in a seperate sub bar plot.
        fig.add_trace(go.Bar(
            x=occupations,
            y=counts,
            name=persona,
            hovertemplate='Occupation: %{x}<br>Count: %{y}',  # When the mouse is over the bar, display additional infos.
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
                {'visible': [persona == selected_persona for selected_persona in personas]},  # Update teh graph with the selected persona.
                {'title': f'Top 20 Actor occupations in relation with the {persona}\'s persona.'}, # Update the title of the graph in function of the new persona selected.
            ]
        } for persona in personas
    ]

    # Update the layout with dropdown to select a persona
    fig.update_layout(
        title=f'Top 20 Actor occupations in relation with the {personas[0]}\'s persona.',
        xaxis_title='Occupations',
        yaxis_title='Count',
        xaxis_tickangle=-45,
        hovermode='closest',
        height=800,
        template="plotly_white",
        updatemenus=[
            {
                'buttons': dropdown_personas_selection,
                'direction': 'down',
                'showactive': True,
                'active': 0,
                'x': 1,
                'xanchor': 'left',
                'y': 1.15,
                'yanchor': 'top',
            }
        ]
    )
    # save the interactive graph in the graphs folder
    fig.write_html("src/graphs/personas_actors_occupations_relations_graph_interactive.html")
    # Show the interactive graph
    fig.show()

