import requests
import urllib2
import base64
from bs4 import BeautifulSoup
import csv, codecs, cStringIO
import string
from collections import defaultdict
import numpy as np

class UTF8Recoder:
    """
    Iterator that reads an encoded stream and reencodes the input to UTF-8
    """
    def __init__(self, f, encoding):
        self.reader = codecs.getreader(encoding)(f)

    def __iter__(self):
        return self

    def next(self):
        return self.reader.next().encode("utf-8")

class UnicodeReader:
    """
    A CSV reader which will iterate over lines in the CSV file "f",
    which is encoded in the given encoding.
    """

    def __init__(self, f, dialect=csv.excel, encoding="utf-8", **kwds):
        f = UTF8Recoder(f, encoding)
        self.reader = csv.reader(f, dialect=dialect, **kwds)

    def next(self):
        row = self.reader.next()
        return [unicode(s, "utf-8") for s in row]

    def __iter__(self):
        return self

class UnicodeWriter:
    """
    A CSV writer which will write rows to CSV file "f",
    which is encoded in the given encoding.
    """

    def __init__(self, f, dialect=csv.excel, encoding="utf-8", **kwds):
        # Redirect output to a queue
        self.queue = cStringIO.StringIO()
        self.writer = csv.writer(self.queue, dialect=dialect, **kwds)
        self.stream = f
        self.encoder = codecs.getincrementalencoder(encoding)()

    def writerow(self, row):
        self.writer.writerow([s.encode("utf-8") for s in row])
        # Fetch UTF-8 output from the queue ...
        data = self.queue.getvalue()
        data = data.decode("utf-8")
        # ... and reencode it into the target encoding
        data = self.encoder.encode(data)
        # write to the target stream
        self.stream.write(data)
        # empty queue
        self.queue.truncate(0)

    def writerows(self, rows):
        for row in rows:
            self.writerow(row)




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


def get_token(client_id, client_secret):
    '''
    Returns a token to use Spotify's API.
    It takes the client id and client secret, provided by Spotify Developer once you create an account.
    INPUT: string, string
    OUTPUT: string
    '''

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

def get_lyrics(musical_title, song_title):
    '''
    Returns the lyrics of a song as a list of lines.
    Searches lyrics on www.stlyrics.com.
    INPUT: string, string
    OUTPUT: list
    '''

    clean_musical = musical_title.lower().replace(' ','')
    clean_song = song_title.lower().replace(' ','')

    url = 'https://www.stlyrics.com/lyrics/%s/%s.htm' %(clean_musical, clean_song)
    soup = BeautifulSoup(urllib2.urlopen(url), 'html.parser')

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

    track_lst = [div.text[1:]for div in divs]

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
            track = row[4]
            spotify_id_to_name[album_id] = musical_title
            spotify_albums_dict[album_id].append(track)

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

    with open ('spotify_correct_albums.csv', 'w') as f1:
        writer_correct = UnicodeWriter(f1)
        with open ('spotify_wrong_albums.csv', 'w') as f2:
            writer_wrong = UnicodeWriter(f2)

            header = ['spotify_id', 'wikipedia_title', 'sp_track', 'track_best_score', 'st_title', 'st_track', 'url']
            writer_correct.writerow(header)
            writer_wrong.writerow(header)
            for spotify_id, wikipedia_title in spotify_id_to_musical.iteritems():
                print wikipedia_title

                spotify_tracks = spotify_id_to_tracks[spotify_id]

                #identifying album stlyrics that I want to compare tracks with
                best_score, st_title = max([(proximity_score(st_title, wikipedia_title), st_title) for st_title in stlyrics_musical_to_tracks.keys()])

                #tracks from stlyrics
                st_tracks = stlyrics_musical_to_tracks[st_title]

                scores_tracks =[]
                for sp_track in spotify_tracks:
                    track_best_score, st_track =max([(proximity_score(sp_track, st_track), st_track) for st_track in st_tracks])
                    scores_tracks.append((track_best_score, st_track, sp_track))


                spotify_album_score = np.mean([x[0] for x in scores_tracks])

                url = 'to_do'
                for track_best_score, st_track, sp_track in scores_tracks:
                    complete_row = [spotify_id, wikipedia_title, sp_track, str(track_best_score),st_title, st_track,url]
                    threshold = 0.6
                    if spotify_album_score > threshold:
                        writer_correct.writerow(complete_row)
                    else:
                        writer_wrong.writerow(complete_row)
                return












def proximity_score(word1, word2):
    '''
    Returns the similarity (0.0 to 1.0) score between two strings.

    INPUT: string, string
    OUTPUT: float
    '''
    ldist = levenshtein(word1,word2)

    similarity = 1.0 - (float(ldist) / max(len(word1), len(word2)))
    return similarity


def levenshtein(s, t):
        ''' From Wikipedia article; Iterative with two matrix rows. '''
        if s == t: return 0
        elif len(s) == 0: return len(t)
        elif len(t) == 0: return len(s)
        v0 = [None] * (len(t) + 1)
        v1 = [None] * (len(t) + 1)
        for i in range(len(v0)):
            v0[i] = i
        for i in range(len(s)):
            v1[0] = i + 1
            for j in range(len(t)):
                cost = 0 if s[i] == t[j] else 1
                v1[j + 1] = min(v1[j] + 1, v0[j + 1] + 1, v0[j] + cost)
            for j in range(len(v0)):
                v0[j] = v1[j]

        return v1[len(t)]






if __name__ == '__main__':
    cross_match()

