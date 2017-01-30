import pandas as pd
import numpy as np
from tfidf_analysis import tfidf_vectors, name_cleaner
from data.lyricist_composer_map import lyricist_map, composer_map

def create_df_music_features_lyrics_labels():
    '''
    Files needed:
    1. spotify_correct_albums_IDs.csv [spotify_id,wikipedia_title,sp_track_id,sp_track,
                                        track_best_score,st_title,st_track,url]

                                        (SP_TRACK_ID, ST_TITLE, ST_TRACK, WIKIPEDIA_TITLE)
                                        8,297
    2. TOTAL_spotify_audio_features2 [album_id,wikipedia_album_name,spotify_album_name,
                                        track_id,track_name,danceability,energy,key,
                                        loudness,mode,speechiness,acousticness,
                                        instrumentalness,liveness,valence,tempo,
                                        duration_ms,time_signature]

                                        (TRACK_ID, MUSIC FEATURES)

    3. stlyrics_musical_tracks_url  [album_name,album_url,track_name,track_url,
                                        track_lyrics,album_type]

                                        (ALBUM_NAME, TRACK NAME, TRACK_LYRICS)


    4. musical_labels.csv [title, year, venue, music, lyrics, book, note]
                            (TITLE, YEAR, MUSIC, LYRICS)

    Creates an array in which each row is a track with the following columns:
    sp_track_id(1) + wikipedia_title(1) + MUSIC FEATURES(13) + year(1) + lyrics(1) +
    label_composers(1) + label_lyricist(1)  = 18 columns

    label = string ex. '1, 7, 9'
    Create a different array which will be label array.
    Each row represents a track and each column is a composer/lyricist.

    '''

    df1_correct = pd.read_csv('spotify_correct_albums_IDs.csv')
    df2_features = pd.read_csv('data/TOTAL_spotify_audio_features2.csv')
    df3_lyrics = pd.read_csv('stlyrics_musical_tracks_url.csv').dropna()
    df4_wikipedia = pd.read_csv('data/musical_labels.csv')

    # neural_nets_input = no
    header = ['sp_track_id', 'wikipedia_title', 'danceability', 'energy','key','loudness',
              'mode','speechiness','acousticness','instrumentalness','liveness','valence',
              'tempo','duration_ms','time_signature', 'year','lyrics', 'composer_label',
              'lyricist_label' ]
    df_music_features_lyrics_labels = pd.DataFrame(columns=header)
    composer_dict = composer_map()
    lyricist_dict = lyricist_map()

    for i, row_correct in df1_correct.iterrows():

        print i
        sp_track_id = row_correct['sp_track_id']
        wikipedia_title = row_correct['wikipedia_title']
        st_title = row_correct['st_title']
        st_track = row_correct['st_track']

        # df1 st_title,st_track
        # df3 album_name, track name
        row_features = df2_features.loc[df2_features['track_id'] == sp_track_id].iloc[0]

        music_features = row_features[5:]
        df_lyrics = df3_lyrics.loc[(df3_lyrics['album_name'] == st_title) &
                                   (df3_lyrics['track_name'] == st_track)]

        if df_lyrics.empty:
            continue

        lyrics = df_lyrics['track_lyrics'].iloc[0]

        df_wikipedia = df4_wikipedia.loc[df4_wikipedia['title'] == wikipedia_title]

        year = df_wikipedia['year'].iloc[0]
        composer = df_wikipedia['music'].iloc[0]
        clean_composer = name_cleaner(composer)
        label_composers = [str(composer_dict[name]) for name in clean_composer]
        string_composers = ','.join(label_composers)

        lyricist = df_wikipedia['lyrics'].iloc[0]
        clean_lyricist = name_cleaner(lyricist)
        label_lyricist = [str(lyricist_dict[name]) for name in clean_lyricist]
        string_lyricists = ','.join(label_lyricist)



        new_row = [sp_track_id, wikipedia_title]
        new_row.extend(music_features)
        new_row.extend([year, lyrics, string_composers, string_lyricists])

        df_music_features_lyrics_labels.loc[len(df_music_features_lyrics_labels)] = new_row



    return df_music_features_lyrics_labels



