import numpy as np
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity

def get_clean_df():
    '''
    Returns a clean dataframe without the song that has no music features.
    INPUT: None
    OUTPUT: dataframe
    '''
    df = pd.read_csv('COMPLETE_DATA.csv')
    #remove NaN row
    df1 = df.drop(df.index[[7410]]).reset_index()
    return df1

def get_lst_musical():
    '''
    Returns a list of musicals and a list of indexes of the songs of musicals.
    INPUT: None
    OUTPUT: list, list
    '''
    df1 = get_clean_df()
    lst_musicals = sorted(df1['wikipedia_title'].unique().tolist())
    musical_index_lst = [df1[df1['wikipedia_title']== musical].index for musical in lst_musicals]

    return lst_musicals, musical_index_lst


def get_musical_matrix(embedding_vectors):
    '''
    Returns the cosine similarity matrix of musicals and the musical embedding vectors.
    INPUT: numpy array
    OUTPUT: numpy array, numpy array
    '''
    lst_musicals, musical_index_lst = get_lst_musical()

    musical_embedding = np.zeros((len(lst_musicals), embedding_vectors.shape[1]))
    for i, index_lst in enumerate(musical_index_lst):
        musical_embedding[i,:] = np.mean(embedding_vectors[index_lst], axis=0)

    musical_distance_matrix = cosine_similarity(musical_embedding)
    return musical_distance_matrix, musical_embedding

def ranked_distance(musical_distance_matrix, musical_index):
    '''
    Returns a list of tuples (musical distance score, index).
    INPUT: numpy array
    OUTPUT: int
    '''
    tuples = [(musical_distance_matrix[musical_index][i], i) for i in xrange(musical_distance_matrix.shape[0])]
    tuples.sort(reverse=True)
    return tuples

def musical_recommender(musical_distance_matrix, musical_name, num_recommendations=5, like=True):
    '''
    Returns a list of musical titles.
    INPUT: numpy matrix, string, int
    OUTPUT: list
    '''

    lst_musicals, musical_index_lst = get_lst_musical() #list of musicals to get title
    musical_index = lst_musicals.index(musical_name) #gets the index of the musical

    musicals_ranked = ranked_distance(musical_distance_matrix, musical_index)
    if like == False:
        return [lst_musicals[index] for score, index in musicals_ranked[-num_recommendations:]]
    return [lst_musicals[index] for score, index in musicals_ranked[1:num_recommendations+1]]

def bad_recommender (musical_distance_matrix, musical_name, num_recommendations=5):
    lst_musicals, musical_index_lst = get_lst_musical()
    musical_index = lst_musicals.index(musical_name)
    musicals_ranked = ranked_distance(musical_distance_embedding, musical_index)
    return [lst_musicals[index] for score, index in musicals_ranked[-num_recommendations:]]