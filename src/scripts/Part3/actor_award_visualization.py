import pandas as pd
import plotly.express as px

def create_actor_award_visualization():
    nb_acteurs = 20
    data = pd.read_csv("src/data/actors_awards_scores.csv", quotechar='"')
    oscars = pd.read_csv("src/data/oscar_clean.csv", quotechar='"')
    data = data.head(nb_acteurs)

    data = data.merge(oscars, how='inner', on='freebase_actor_id')
    data = data.dropna(subset=['CanonicalCategory'])
    data = data.dropna(subset=['Class'])
    data = data.dropna(subset=['Actor'])

    # Create a sunburst chart with Plotly
    print(data)
    fig = px.sunburst(
        data,
        path=['Actor', 'Class', 'CanonicalCategory'],  # Define the hierarchy
        values='score',  # Size of each segment
        color='Class',  # Use category to determine color,
        title='Actors and Their Awards by Category and Subcategory',
        width=1800, height=1600
    )


    fig.show()
    # # Export the figure to an HTML file to share
    # fig.write_html("/mnt/data/Actors_Awards_Sunburst.html")
