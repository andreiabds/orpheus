import base64
from bs4 import BeautifulSoup
from collections import defaultdict
import numpy as np
import os
import requests
import string
import time
import urllib2
from utils import *
from string_utils import *



def get_album_info(album_name):
    '''
    Returns a list with all Spotify album ids and name that match with the given album name.
    INPUT: string
    OUTPUT: list of tuples [(album_id, album_name)]
    '''

    album_name = album_name.replace(' ', '%20').encode('UTF-8')
    response = requests.get('https://api.spotify.com/v1/search?q=album:%s*&type=album' % album_name)
    data = response.json()
    album_info = [(album['id'], album['name']) for album in data['albums']['items']]
    return album_info


def get_track_data(album_id):
    '''
    Returns a list with Spotify track data (id, title, track number and duration) from a given album id.

    INPUT: string
    OUTPUT: list of tuples [(track_id, track_title, track_number, track_duration)]
    '''

    response = requests.get('https://api.spotify.com/v1/albums/%s/tracks' % album_id)
    data = response.json()
    track_data = [(track['id'], track['name'], track['track_number'], track['duration_ms']) for track in data['items']]

    return track_data


def get_token():
    '''
    Returns a token to use Spotify's API.
    It takes the client id and client secret, provided by Spotify Developer once you create an account.
    INPUT: string, string
    OUTPUT: string
    '''
    client_id = os.environ['SPOTIFY_CLIENT_ID']
    client_secret = os.environ['SPOTIFY_CLIENT_SECRET']

    auth_header = base64.b64encode(client_id + ':' + client_secret)


    headers = {'Authorization': 'Basic %s' % auth_header}
    payload = {'grant_type': 'client_credentials'}

    r = requests.post('https://accounts.spotify.com/api/token', data=payload, headers=headers)

    token = r.json()['access_token']

    return token

def get_audio_features(track_id, token):
    '''
    Returns a json object containing the audio features of a given song track.
    audio features

    INPUT: string, string
    OUTPUT: json object

    example:
            {
          "danceability" : 0.735,
          "energy" : 0.578,
          "key" : 5,
          "loudness" : -11.840,
          "mode" : 0,
          "speechiness" : 0.0461,
          "acousticness" : 0.514,
          "instrumentalness" : 0.0902,
          "liveness" : 0.159,
          "valence" : 0.624,
          "tempo" : 98.002,
          "type" : "audio_features",
          "id" : "06AKEBrKUckW0KREUWRnvT",
          "uri" : "spotify:track:06AKEBrKUckW0KREUWRnvT",
          "track_href" : "https://api.spotify.com/v1/tracks/06AKEBrKUckW0KREUWRnvT",
          "analysis_url" : "https://api.spotify.com/v1/audio-analysis/06AKEBrKUckW0KREUWRnvT",
          "duration_ms" : 255349,
          "time_signature" : 4
        }
    '''

    headers = {'Authorization': 'Bearer %s' % token}
    r = requests.get('https://api.spotify.com/v1/audio-features/%s' % track_id, headers=headers)

    return r.json()

def get_lyrics(musical_title=None, song_title=None, url=None):
    '''
    Returns the lyrics of a song as a list of lines.
    Searches lyrics on www.stlyrics.com.
    INPUT: string, string
    OUTPUT: list
    '''
    if not (musical_title and song_title) and not url:
        return

    if musical_title and song_title:
        clean_musical = musical_title.lower().replace(' ','')
        clean_song = song_title.lower().replace(' ','')

    if not url:
        url = 'https://www.stlyrics.com/lyrics/%s/%s.htm' %(clean_musical, clean_song)

    print '\t%s' % url

    try:
        track_webpage = urlopen_with_retry(url)
    except urllib2.HTTPError:
        # Not found.
        return []

    soup = BeautifulSoup(track_webpage, 'html.parser')

    divs = soup.find("div", {"class": "col-xs-11 main-text"}).findAll('div')

    lines =[div.text for div in divs]

    return lines



def wikipedia_musicals():


    with open ('wikipedia_list.csv', 'w') as wiki:
        for filename in ('lst_musicals%d.htm' % i for i in [1,2]):
            f = open(filename)
            html_doc = f.read()
            soup = BeautifulSoup(html_doc, 'html.parser')

            for table in soup.find_all('table'):
                for tr in table.find_all('tr')[2:]:
                    musical = tr.find_all('td')[0].get_text()
                    musical = musical.split('\n')[0].encode('UTF-8')
                    wiki.write(musical +'\n')


def list_of_musical_albums(musicals_name):

    #fix later
    musicals_name = wikipedia_musicals()

    with open('musical_id.csv', 'w') as f:
        csv_writer = csv.writer(f)
        with open ('missing_musical.csv', 'w') as missing:
            counter = 0
            for musical in musicals_name:
                if counter%10 == 0:
                    print counter
                album_ids = get_album_info(musical)
                musical = musical.encode('UTF-8')
                if not album_ids:
                    missing.write(musical + '\n')
                    missing.flush()
                all_album_ids.extend(album_ids)
                csv_writer.writerows([[x, musical, title.encode('UTF-8')] for x, title in album_ids])
                counter += 1

def create_track_csv():
    with open ('tracks_musicals.csv', 'w') as f_tracks:
        with open('data/LIST_musicals_albums.csv') as f:
            reader = UnicodeReader(f)
            writer = UnicodeWriter(f_tracks)
            writer.writerow(['album_id', 'wikipedia_album_name', 'spotify_album_name',
                'track_id', 'track_name', 'track_number', 'track_duration_ms'])

            for row in reader:
                album_id = row[0]
                album_tracks = get_track_data(album_id)
                for track in album_tracks:
                    lst_track = row + list(track)
                    u_lst_track = [unicode(i) for i in lst_track]
                    writer.writerow(u_lst_track)





def create_album_csv_stlyrics():
    '''
    Creates a csv file with all album titles, url, and type from www.stlyrics.com (lyrics website).
    INPUT: none
    OUTPUT: csv
    '''
    with open ('lyrics_web_albums.csv', 'w') as all_lyrics_albums:

        writer = UnicodeWriter(all_lyrics_albums)
        writer.writerow(['album_title', 'album_url', 'album_type'])
        alphabet = list(string.ascii_lowercase)
        url_lst =['https://www.stlyrics.com/%s.htm' % s for s in alphabet + ['19']]

        for url in url_lst:
            print url
            soup = BeautifulSoup(urllib2.urlopen(url), 'html.parser')
            a_elements = soup.find("div", {"class": "list-group soundtrackA"}).findAll('a')


            for a in a_elements:
                album_url = a['href']
                div = a.div
                album_type = div.img['alt']
                album_title = div.find("span", {"class": "soundtrackAtext"}).text[:-7]
                row = [album_title, album_url, album_type]
                writer.writerow(row)


def tracks_from_lyrics_website(album_name, url=None):
    '''
    Returns a list of track names from a given album.

    INPUT: string
    OUTPUT: list

    '''
    if not url:
        clean_album = album_name.lower().replace(' ','')
        url = 'https://www.stlyrics.com/%s/%s.htm' % (clean_album[0], clean_album)
    soup = BeautifulSoup(urllib2.urlopen(url), 'html.parser')
    divs = soup.findAll("div", {"class": "h4"})[:-1]

    track_lst = [div.text[1:] for div in divs]

    return track_lst



def scrape_tracks_stlyrics():
    with open ('tracks_stlyrics.csv', 'w') as tracks_stlyrics:
        with open ('data/stlyrics_albums.csv', 'r') as st_albums:
            reader = UnicodeReader(st_albums)
            writer = UnicodeWriter(tracks_stlyrics)

            for i, row in enumerate(reader):
                if i == 0:
                    continue
                item_type = row[2]
                if item_type != 'musical':
                    continue

                musical_title = row[0]
                url = row[1]

                tracks = tracks_from_lyrics_website(musical_title, url=url)
                complete_row = [musical_title] + tracks
                writer.writerow(complete_row)
                print i, musical_title


def read_stlyrics_tracks_csv():
    with open ('data/tracks_stlyrics.csv', 'r') as tracks_stlyrics:
        reader = UnicodeReader(tracks_stlyrics)

        d ={}
        for row in reader:
            musical_title = row[0]
            track_names = row[1:]
            d[musical_title] = track_names

    return d

def make_dicts_spotify_albums():
    spotify_albums_dict = defaultdict(list)
    spotify_id_to_name = {}
    with open ('data/spotify_all_tracks_musicals.csv', 'r') as tracks_spotify:
        reader = UnicodeReader(tracks_spotify)

        for row in reader:
            album_id = row[0]
            musical_title = row[1]
            track_name = row[4]
            track_id = row[3]
            spotify_id_to_name[album_id] = musical_title
            spotify_albums_dict[album_id].append((track_name,track_id))

    return spotify_id_to_name, spotify_albums_dict



def cross_match():
    '''
    Creates two csv files (spotify_correct_albums, spotify_wrong_albums).
    First the function checks the title of the spotify album to the most similar title on stlyrics.com.
    Then, it compares how similar the track names are between spotify and stlyrics.com.
    If the average similarity is above a certain threshold, we consider the album to be a musical.
    Else, we consider it to not be a musical.

    Columns on the csv:
    spotify_id, wikipedia_title, sp_track, track_best_score, st_title, st_track,url

    '''
    spotify_id_to_musical, spotify_id_to_tracks = make_dicts_spotify_albums()
    stlyrics_musical_to_tracks = read_stlyrics_tracks_csv()

    with open ('spotify_correct_albums_IDs.csv', 'w') as f1:
        writer_correct = UnicodeWriter(f1)
        with open ('spotify_wrong_albums_IDs.csv', 'w') as f2:
            writer_wrong = UnicodeWriter(f2)

            header = ['spotify_id', 'wikipedia_title', 'sp_track_id', 'sp_track',
                        'track_best_score', 'st_title', 'st_track', 'url']
            writer_correct.writerow(header)
            writer_wrong.writerow(header)
            count = 0
            for spotify_id, wikipedia_title in spotify_id_to_musical.iteritems():
                count += 1
                print count, wikipedia_title

                spotify_tracks_names_and_id = spotify_id_to_tracks[spotify_id]

                #identifying album stlyrics that I want to compare tracks with
                best_score, st_title = max([(proximity_score(st_title, wikipedia_title), st_title) for st_title in stlyrics_musical_to_tracks.keys()])

                #tracks from stlyrics
                st_tracks = stlyrics_musical_to_tracks[st_title]

                scores_tracks =[]
                for sp_track, sp_track_id in spotify_tracks_names_and_id:
                    track_best_score, st_track =max([(proximity_score(sp_track, st_track), st_track) for st_track in st_tracks])
                    scores_tracks.append((track_best_score, st_track, sp_track, sp_track_id))


                spotify_album_score = np.mean([x[0] for x in scores_tracks])

                url = 'to_do'
                for track_best_score, st_track, sp_track, sp_track_id in scores_tracks:
                    complete_row = [spotify_id, wikipedia_title, sp_track_id, sp_track, str(track_best_score),st_title, st_track,url]
                    threshold = 0.5
                    if spotify_album_score > threshold:
                        writer_correct.writerow(complete_row)
                    else:
                        writer_wrong.writerow(complete_row)






def create_csv_audio_features():
    '''
    Creates a csv file with all audio features from spotify.
    '''
    token = get_token()
    token_time = time.time()
    refresh_time = 45*60

    keys = ["danceability", "energy", "key", "loudness","mode", "speechiness",
            "acousticness", "instrumentalness", "liveness", "valence", "tempo",
            "duration_ms", "time_signature"]
    header = ["album_id", "wikipedia_album_name", "spotify_album_name", "track_id",
            "track_name"] + keys

    with open ('data/spotify_all_tracks_musicals.csv', 'r') as f_all_tracks:
        reader_track = UnicodeReader(f_all_tracks)
        with open ('spotify_audio_features2.csv', 'w') as f_audio_features:
            writer_audio_features = UnicodeWriter(f_audio_features)
            writer_audio_features.writerow(header)

            for i, row in enumerate(reader_track):
                print i, row[2], row[4]
                if i < 3312:
                    continue
                if (time.time() - token_time) > refresh_time:
                    token = get_token()
                    token_time = time.time()
                track_id = row[3]
                features = get_audio_features(track_id, token)
                keys = ["danceability", "energy", "key", "loudness","mode", "speechiness",
                        "acousticness", "instrumentalness", "liveness", "valence", "tempo",
                        "duration_ms", "time_signature"]
                track_features = [str(features.get(key, 'nan')) for key in keys]
                info = row[0:5]
                complete_row = info + track_features
                writer_audio_features.writerow(complete_row)

def musical_labels():

    with open ('musical_labels.csv', 'w') as wiki:
        writer = UnicodeWriter(wiki)
        header = ['title', 'year', 'venue', 'music', 'lyrics', 'book', 'notes']
        writer.writerow(header)
        for filename in ('lst_musicals%d.htm' % i for i in [1,2]):
            f = open(filename)
            html_doc = f.read()
            soup = BeautifulSoup(html_doc, 'html.parser')


            for table in soup.find_all('table'):
                for tr in table.find_all('tr')[2:]:
                    lst_row = [td.get_text().split('\n')[0] for td in tr.find_all('td')]
                    writer.writerow(lst_row)



def musicals_tracks_url_stlyrics():
    with open ('data/stlyrics_albums.csv', 'r') as f_albums_stlyrics:
        reader_albums = UnicodeReader(f_albums_stlyrics)

        with open ('stlyrics_musical_tracks_url.csv', 'w') as f_tracks_url:
            writer_tracks = UnicodeWriter(f_tracks_url)

            header = ['album_name', 'album_url', 'track_name', 'track_url', 'track_lyrics', 'album_type']

            writer_tracks.writerow(header)

            beginning_url = 'https://www.stlyrics.com'
            for i, row in enumerate(reader_albums):
                print i
                if i == 0:
                    continue
                album_name = row[0]
                album_url = row[1]
                album_type = row[2]

                if album_type != 'musical':
                    continue

                print album_url
                album_webpage = urlopen_with_retry(album_url)
                soup = BeautifulSoup(album_webpage, 'html.parser')

                divs = soup.findAll("div", {"class": "h4"})[:-1]

                for i, div in enumerate(divs):
                    track_name = div.text[1:]
                    end_track_url = div.parent.get('href')
                    if not end_track_url:
                        track_url = ''
                        track_lyrics = ''
                    else:
                        track_url = beginning_url + end_track_url
                        track_lyrics =  get_lyrics(url=track_url)
                        track_lyrics = ' '.join(line.strip() for line in track_lyrics)

                    writer_tracks.writerow([album_name, album_url, track_name, track_url, track_lyrics, album_type])


if __name__ == '__main__':
    cross_match()

