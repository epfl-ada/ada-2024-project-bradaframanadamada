import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

nb_actors = 20
oscars = pd.read_csv("src/data/oscar_clean.csv", quotechar='"')

def process_data(data):
    data = data.head(nb_actors)
    data = data.rename(columns={'name': 'Actor'})
    data = data.merge(oscars, how='inner', on='freebase_actor_id')
    data = data.dropna(subset=['CanonicalCategory'])
    data = data.dropna(subset=['Class'])
    data = data.dropna(subset=['Actor'])
    data = data.assign(Count=1)
    return data.groupby(['Actor', 'Class', 'CanonicalCategory']).sum().reset_index()


def create_actor_award_visualization():
    data1 = pd.read_csv("src/data/actors_awards_scores.csv", quotechar='"')
    data2 = pd.read_csv("src/data/actors_success.csv", quotechar='"')
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
    data1 = process_data(data1)
    data2 = process_data(data2)

    # Create labels and parents for the sunburst hierarchy

    fig = go.Figure()

    fig1 = px.sunburst(
        data1,
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

    fig2  = px.sunburst(
        data2,
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


    fig.add_trace(fig1.data[0])
    fig.add_trace(fig2.data[0])

    fig.data[0].visible = True
    fig.data[1].visible = False

    fig.update_layout(
        updatemenus=[
            dict(
                buttons=[
                    dict(
                        label="Awards Score",
                        method="update",
                        args=[{"visible": [True, False]},  # Show first, hide second
                              {"title": "Oscar Nominations and Wins Analysis<br><sub>Comparing the top 20 actors based on Oscar achievements</sub>"}]
                    ),
                    dict(
                        label="Opinion Score",
                        method="update",
                        args=[{"visible": [False, True]},  # Hide first, show second
                              {"title": "Oscar Nominations and Wins Analysis<br><sub>Comparing the top 20 actors based on public opinion</sub>"}]
                    )
                ],
                direction="down",
                showactive=True,
                x=0.5,
                xanchor="center",
                y=1.2
            )
        ]
    )

    fig.update_layout(
        title={
            "text": "Oscar Nominations and Wins Analysis<br><sub>Comparing the top 20 actors based on Oscar achievements</sub>",
            "x": 0.5,
            "xanchor": "center",
            "yanchor": "top"
        },
        annotations=[
            dict(
                text="Opinion Score: Top 20 actors based on public opinion | Awards score: Top 20 actors based on Oscar archievement",
                x=0.5, y=-0.15,  # Place below the chart
                xref="paper", yref="paper",
                showarrow=False,
                font=dict(size=12, color="gray")
            )
        ],
        margin=dict(t=120, l=50, r=50, b=150),  # Adjust margins for better spacing
        width=1000,  # Chart width
        height=900,  # Chart height
        template="plotly_white",  # Clean template
        font=dict(family="Arial, sans-serif", size=14, color="black")  # Global font style
    )

    fig.show()
    # # Export the figure to an HTML file to share
    #fig.write_html("src/graphs/Actors_Awards_Sunburst.html")



