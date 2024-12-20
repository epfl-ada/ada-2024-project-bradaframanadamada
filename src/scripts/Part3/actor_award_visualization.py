import pandas as pd
import plotly.express as px

def create_actor_award_visualization():
    nb_acteurs = 20
    data = pd.read_csv("src/data/actors_awards_scores.csv", quotechar='"')
    oscars = pd.read_csv("src/data/oscar_clean.csv", quotechar='"')
    data = data.head(nb_acteurs)

    # Create a sunburst chart with Plotly
    color_mapping = {
        "(?)":"#AED6F1"  ,
        "Title": "#FFC1CC",  # Rose poudré
        "Acting": "#A4DDED",  # Bleu ciel pastel
        "Directing": "#D6BBFC",  # Lavande légère
        "Writing": "#FFDAB9",  # Pêche pâle
        "Music": "#FFFACD",  # Jaune crème doux
        "Production": "#C7F9CC",  # Menthe fraîche
        "SciTech": "#BFE3C4",  # Vert sauge pastel
        "Special": "#EEDCFB"  # Mauve délicat
    }


    data = data.merge(oscars, how='inner', on='freebase_actor_id')
    data = data.dropna(subset=['CanonicalCategory'])
    data = data.dropna(subset=['Class'])
    data = data.dropna(subset=['Actor'])
    data = data.assign(Count=1)
    data = data.groupby(['Actor', 'Class', 'CanonicalCategory']).sum().reset_index()




    fig = px.sunburst(
        data,
        path=['Actor', 'Class', 'CanonicalCategory'],  # Define the hierarchy
        values='score',  # Size of each segment
        color='Class',  # Use category to determine color,
        color_discrete_map= color_mapping,
        title='Actors and Their Awards by Category and Subcategory',
        hover_data={"Actor": True,
                "CanonicalCategory":True,
                "Class":True,
                "Winner":True,
                "Count":True,
                "score": False},
        template="plotly_white",
        width=1800, height=1600
    )


    fig.show()
    # # Export the figure to an HTML file to share
    # fig.write_html("/mnt/data/Actors_Awards_Sunburst.html")
