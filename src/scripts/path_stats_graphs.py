import numpy as np
import pandas as pd
from tqdm import tqdm
import plotly.graph_objects as go
import os.path
from compute_distance_matrix import compute_distance_matrix_with_mode

def compute_df_for_k_nearest_neighbors_n_most_popular_actors(sorting_id, k, n, df_score, df_merged):
    """
    compute a dataframe containing the k nearest paths for each of the n most popular actors
    @param sorting_id: ids to sort each line the distance matrix computed for the df_merged dataframe (np.argsort(axis=1))
    @param k: number of nearest neighbors (excluding the actor itself)
    @param n: the number of actors to consider, take the n with the highest score
    @param df_score: dataframe containing:
            a 'score' column representing the metric score
            a 'freebase_actor_id' column representing the freebase actor id
    @param df_merged: dataframe containing:
            a 'score' column representing the metric score
            a 'freebase_actor_id' column representing the freebase actor id
            an 'Actor name' column containing the names of the actors

    @return: dataframe containing the information of df_merged for each set of k neighbors, extended with:
            a 'base actor' column containing the name of the actor the paths are close to
            a 'base id' column containing the freebase actor id of the base actor
    """
    highest_n = df_score.nlargest(n, 'score')
    set_ids = set(highest_n['freebase_actor_id'])
    top_k = sorting_id[:, 1:k+1]
    df_list = []
    for i in tqdm(range(top_k.shape[0])):
        sim_df = df_merged.iloc[top_k[i]].copy()
        sim_df['base actor'] = df_merged.iloc[i]['Actor name']
        sim_df['base id'] = df_merged.iloc[i]['freebase_actor_id']
        df_list.append(sim_df)
    df_prox = pd.concat(df_list)
    filtered_prox = df_prox[df_prox['base id'].isin(set_ids)]
    return filtered_prox

def compute_df_for_d_distance_n_most_popular_actors(distance_matrix, d, n, df_score, df_merged):
    """
    compute a dataframe containing the paths at distance < d (not including the actor itself) for each of the n most popular actors
    @param distance_matrix: distance matrix computed for the df_merged dataframe
    @param d: distance threshold
    @param n: number of actors that will be considered, take the n with the highest score
    @param df_score: dataframe containing:
            a 'score' column representing the metric score
            a 'freebase_actor_id' column representing the freebase actor id
    @param df_merged: dataframe containing:
            a 'score' column representing the metric score
            a 'freebase_actor_id' column representing the freebase actor id
            an 'Actor name' column containing the names of the actors
    @return: dataframe containing the information of df_merged for each set neighbors with distance < d, extended with:
            a 'base actor' column containing the name of the actor the paths are close to
            a 'base id' column containing the freebase actor id of the base actor
    """
    highest_n = df_score.nlargest(n, 'score')
    set_ids = set(highest_n['freebase_actor_id'])
    df_list = []
    for i in tqdm(range(distance_matrix.shape[0])):
        is_close = distance_matrix[i] < d
        is_close[i] = False
        sim_df = df_merged.loc[is_close].copy()
        sim_df['base actor'] = df_merged.iloc[i]['Actor name']
        sim_df['base id'] = df_merged.iloc[i]['freebase_actor_id']
        df_list.append(sim_df)
    df_prox = pd.concat(df_list)
    filtered_prox = df_prox[df_prox['base id'].isin(set_ids)]
    return filtered_prox

def path_graph_k_neighbors(sorting_id, n, df_score, df_merged, mode, start=10, stop=101, stride=10):
    """
    create a plotly graph presenting the stats of k nearest paths for the n most successful actors with a slider on k.
    save it in '../graphs/K_neighbor_career_paths_{mode}.html'
    @param sorting_id: ids to sort each line the distance matrix computed for the df_merged dataframe (np.argsort(axis=1))
    @param n: number of actors that will be plotted, take the n with the highest score
    @param df_score: dataframe containing:
            a 'score' column representing the metric score
            a 'freebase_actor_id' column representing the freebase actor id
    @param df_merged: dataframe containing:
            a 'score' column representing the metric score
            a 'freebase_actor_id' column representing the freebase actor id
            an 'Actor name' column containing the names of the actors
    @param mode: text for labelization and file naming, can be 'award' or 'success'
    @param start: start of slider range, default 10
    @param stop: stop of slider range, default 101
    @param stride: step between each slider values, default 10
    """
    fig = go.Figure()
    for step in np.arange(start, stop, stride):
        df_plot = compute_df_for_k_nearest_neighbors_n_most_popular_actors(sorting_id, step, n, df_score, df_merged)
        fig.add_trace(
            go.Box(x=df_plot['base actor'],
                   y=df_plot['score'],
                   visible=False,
                   name=f'{mode} score distribution of the k={step} nearest career paths for top {n} actors'
                   )
        )
    fig.data[0].visible = True

    # Create and add slider
    steps = []
    for i in tqdm(range(len(fig.data))):
        step = dict(
            method="update",
            args=[{"visible": [False] * len(fig.data)},
                  {
                      "title": f'{mode} score distribution of the k={i*stride + start} nearest career paths for top {n} actors'}],
            # layout attribute
        )
        step["args"][0]["visible"][i] = True  # Toggle i'th trace to "visible"
        steps.append(step)

    sliders = [dict(
        active=10,
        pad={"t": 120},
        steps=steps
    )]

    fig.update_layout(
        sliders=sliders
    )
    # make y axis log only for success mode as the score have a huge magnitude
    if mode == 'success':
        fig.update_yaxes(type="log")
    fig.update_layout(title=dict(
        text=f'{mode} score distribution of the k={start} nearest career paths for top {n} actors'
    ),
        yaxis=dict(
            title=dict(
                text=f'{mode} score'
            )
        ))
    fig.write_html(f'../graphs/K_neighbor_career_paths_{mode}.html')

def path_graph_d_distance(distance_matrix, n, df_score, df_merged, mode, start=15, stop=18, stride=1):
    """
    create a plotly graph presenting the stats of the paths at distance < d for the n most successful actors with a slider on d.
    save it in '../graphs/d_distance_career_paths_{mode}.html'
    @param distance_matrix: distance matrix computed for the df_merged dataframe
    @param n: number of actors that will be plotted, take the n with the highest score (will plot less if no neighbor is found for some base actors)
    @param df_score: dataframe containing:
            a 'score' column representing the metric score
            a 'freebase_actor_id' column representing the freebase actor id
    @param df_merged: dataframe containing:
            a 'score' column representing the metric score
            a 'freebase_actor_id' column representing the freebase actor id
            an 'Actor name' column containing the names of the actors
    @param mode: text for labelization and file naming, can be 'award' or 'success'
    @param start: start of slider range, default 15 (if too small, the first frames will be empty)
    @param stop: end of slider range, default 18 (if too big, the dataframe will be too big, possibly causing memory errors)
    @param stride: step between each slider values, default 1
    """
    fig = go.Figure()
    for step in np.arange(start, stop, stride):
        df_plot = compute_df_for_d_distance_n_most_popular_actors(distance_matrix, step, n, df_score, df_merged)
        fig.add_trace(
            go.Box(x=df_plot['base actor'],
                   y=df_plot['score'],
                   visible=False,
                   name=f'{mode} score distribution of the career paths at distance < {step} for top {n} actors'
                   )
        )
    fig.data[0].visible = True

    # Create and add slider
    steps = []
    for i in tqdm(range(len(fig.data))):
        step = dict(
            method="update",
            args=[{"visible": [False] * len(fig.data)},
                  {
                      "title": f'{mode} score distribution of the career paths at distance < {start + i*stride} for top {n} actors'}],
            # layout attribute
        )
        step["args"][0]["visible"][i] = True  # Toggle i'th trace to "visible"
        steps.append(step)

    sliders = [dict(
        active=10,
        pad={"t": 120},
        steps=steps
    )]

    fig.update_layout(
        sliders=sliders
    )
    # make y axis log only for success mode as the score have a huge magnitude
    if mode == 'success':
        fig.update_yaxes(type="log")
    fig.update_layout(title=dict(
        text=f'{mode} score distribution of the career paths at distance < {start} for top {n} actors'
    ),
        yaxis=dict(
            title=dict(
                text=f'{mode} score'
            )
        ))
    fig.write_html(f'../graphs/d_distance_career_paths_{mode}.html')

if __name__ == '__main__':
    # define number of successful actors to plot
    n = 30

    # load paths data
    df_paths = pd.read_pickle('../data/clean_careers_paths.pkl')

    # load success data
    if not os.path.exists('../data/distance_matrix_success.txt'):
        print('success matrix not found, generating...')
        compute_distance_matrix_with_mode('success')
    success_matrix = np.loadtxt('../data/distance_matrix_success.txt', delimiter=',')
    print('successfully loaded success distance matrix')
    df_success = pd.read_csv('../data/actors_success.csv')
    df_merged_success = df_paths.reset_index()[['Actor name', 'personas_list', 'freebase_actor_id']].merge(
        df_success[['freebase_actor_id', 'score']])
    # get sorting ids for success distance matrix
    sorting_ids_success = success_matrix.argsort(axis=1)
    # success graphs
    path_graph_k_neighbors(sorting_ids_success, n, df_success, df_merged_success, 'success')
    path_graph_d_distance(success_matrix, n, df_success, df_merged_success, 'success')

    # load award data
    if not os.path.exists('../data/distance_matrix_award.txt'):
        print('award matrix not found, generating...')
        compute_distance_matrix_with_mode('award')
    award_matrix = np.loadtxt('../data/distance_matrix_award.txt', delimiter=',')
    print('successfully loaded award distance matrix')
    df_award = pd.read_csv('../data/actors_awards_scores.csv')
    df_merged_award = df_paths.reset_index()[['Actor name','personas_list', 'freebase_actor_id']].merge(df_award[['freebase_actor_id', 'score']])
    # get sorting ids for award distance matrix
    sorting_ids_award = award_matrix.argsort(axis=1)
    # award graphs
    path_graph_k_neighbors(sorting_ids_award, n, df_award, df_merged_award, 'award')
    path_graph_d_distance(award_matrix, n, df_award, df_merged_award, 'award')


