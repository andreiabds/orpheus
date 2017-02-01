import numpy as np
from numpy import *
from numpy import linalg as la
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity

def ecludSim(inA, inB):
    return 1.0/(1.0 + la.norm(inA - inB))

def pearsSim(inA, inB):
    if len(inA) < 3 : return 1.0
    return 0.5+0.5*corrcoef(inA, inB, rowvar=0)[0][1]

def cosSim(inA, inB):
    num = float(inA.T*inB)
    denom = la.norm(inA) * la.norm(inB)
    return 0.5+0.5*(num/denom)



def get_name_song_from_index(index_num):
    df1 = pd.read_csv('COMPLETE_AWESOME_DATA.csv')
    df2 = pd.read_csv('spotify_correct_albums_IDs.csv')

    track_id = df1.iloc[index_num]['sp_track_id']
    track_name = df2[df2['sp_track_id'] == track_id]['sp_track'].iloc[0]
    return track_name


'''
Start an empty matrix (songs x songs) (7816, 7816)

Embeddings numpy.array songs x k (7816, 64)

#curse of dimensionality ...too many features

Next STEP
Auto encoder

Start with first layer
pass in your song and try to predict song again!
cost function RMSE

Output

Step back to original data


'''

#keep track of index of embedding vector (e.g., know which song is which row)
df1 = pd.read_csv('COMPLETE_AWESOME_DATA.csv')
df2 = pd.read_csv('spotify_correct_albums_IDs.csv')

#use track_id to get track_name for smell test
df2 = pd.read_csv('spotify_correct_albums_IDs.csv')


#Create empty numpy matrix

NUM_SONGS = df1.shape[0]
similarity_matrix = np.zeros((NUM_SONGS, NUM_SONGS))

for i_1, song_embedding_1 in enumerate(embedding):
    for i_2, song_embedding_2 in enumerate(embedding):
        similarity_matrix[i_1:i_2] = cosine_similarity(i_1, i_2)[0][0]


