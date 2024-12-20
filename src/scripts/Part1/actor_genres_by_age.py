def plot_genres_over_age_with_dropdown(actor_dfs, nb_genres):
    """
    This function creates a histogram with density curves for multiple actors, with a dropdown to select an actor.

    Parameters:
    - actor_dfs: A dictionary where keys are actor names and values are their corresponding DataFrames.
    - nb_genres: The number of genres.
    """
    fig = go.Figure()

    dropdown_buttons = []
    for idx, (actor_name, actor_df) in enumerate(actor_dfs.items()):
        # Process the actor DataFrame
        genres_df = actor_df[['Actor age at movie release', 'Movie genres']]
        genres_df = genres_df.explode('Movie genres')

        #Select only the top NB_GENRES genres
        top_genres = (
            genres_df.groupby('Movie genres').count()
            .sort_values('Actor age at movie release', ascending=False)
            .index[:nb_genres]
        )
        genres_df = genres_df[genres_df['Movie genres'].isin(top_genres)]
        genres_lists = genres_df.groupby('Movie genres')['Actor age at movie release'].apply(list)

        # Compute the number of pairs 'Actor age' and 'Movie genre'
        genres_df_grouped = genres_df.groupby(
            ['Actor age at movie release', 'Movie genres']
        ).size().reset_index()

        # Track colors for genres
        color_map = {}

        # Create histogram traces for this actor
        histogram_traces = []
        for genre in top_genres:

            color = px.colors.qualitative.Plotly[top_genres.tolist().index(genre) % len(px.colors.qualitative.Plotly)]
            color_map[genre] = color  # Map the color for this genre

            genre_data = genres_df_grouped[genres_df_grouped['Movie genres'] == genre]
            trace = go.Histogram(
                x=genre_data['Actor age at movie release'],
                y=genre_data[0],
                name=genre,
                opacity=0.5,
                visible=(idx == 0),  # Only the first actor's data is initially visible
                #legendgroup=f"group-{actor_name}",
                showlegend=False,
                marker=dict(color=color)
            )
            histogram_traces.append(trace)
            fig.add_trace(trace)

        # Add density curve traces for this actor
        for genre, ages in genres_lists.items():
            kde = gaussian_kde(ages)
            x = np.linspace(min(ages), max(ages), 100)
            y = kde(x) * len(ages)  # Scale KDE to match histogram counts

            curve_trace = go.Scatter(
                x=x,
                y=y,
                mode='lines',
                name=genre,
                visible=(idx == 0),  # Only the first actor's data is initially visible
                legendgroup=f"group-{actor_name}",
                line=dict(color=color_map[genre], width=2)
            )
            fig.add_trace(curve_trace)

        # Add violin plot traces for this actor
        for id, (genre, ages) in enumerate(genres_lists.items()):
            box_trace = go.Violin(
                x=ages,
                y0=7-id+nb_genres,
                name=genre,
                visible=(idx == 0),  # Only visible for the first actor initially
                marker=dict(color=color_map[genre]),
                opacity=0.5,
                showlegend=False
            )
            fig.add_trace(box_trace)

        # Add dropdown button for this actor
        dropdown_buttons.append({
            'label': actor_name,
            'method': 'update',
            'args': [
                {'visible': [i//(3*nb_genres) == idx for i in range(len(actor_dfs) * 3 * nb_genres)]}#,
                #{'title': f"Actor Age Distribution for {actor_name}"}
            ]
        })

    # Update layout with dropdown
    fig.update_layout(
        updatemenus=[
            {
                'buttons': dropdown_buttons,
                'direction': 'down',
                'showactive': True,
                'x': 1.15,
                'xanchor': 'right',
                'y': 1.15,
                'yanchor': 'top',
            }
        ],
        title="Movie genres over actor age",
        xaxis_title="Actor age",
        yaxis_title="Number of films labeled with the corresponding genre",
        width=1200,
        height=600
    )

    # Save the plot
    fig.write_html("../../graphs/actors_preferred_genres_by_age.html")

if __name__ == "__main__":
    import pandas as pd
    import plotly.express as px
    import plotly.graph_objects as go
    from scipy.stats import gaussian_kde
    import numpy as np

    # Import DataFrames and drop possible NaN # This is your Project Root
    cmu_df = pd.read_pickle("../../data/metadata_cmu.pkl")
    cmu_df = cmu_df.dropna(subset=["Actor age at movie release"])
    actor_success_df = pd.read_csv("../../data/actors_success.csv")

    actor_success_df.rename(columns={'freebase_actor_id':'Freebase actor ID'}, inplace=True)

    NB_GENRES = 5
    NB_ACTORS = 50

    # Get the NB_ACTORS most popular actors
    most_popular_actors_list = actor_success_df.sort_values("score", ascending=False)[:NB_ACTORS]
    actors_df = cmu_df.loc[cmu_df['Freebase actor ID'].isin(most_popular_actors_list['Freebase actor ID'].values)]

    # Compute a dict for each actor
    actors_dict = {}
    for actor_id in most_popular_actors_list['Freebase actor ID']:
        actor_df = cmu_df[cmu_df['Freebase actor ID'] == actor_id]
        actors_dict[actor_df['Actor name'].iloc[0]] = actor_df[['Actor age at movie release', 'Movie genres']]

    # Call the plot function
    plot_genres_over_age_with_dropdown(actors_dict, NB_GENRES)