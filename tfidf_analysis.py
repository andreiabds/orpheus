import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from string import punctuation
from nltk.stem.porter import PorterStemmer
from nltk.stem.snowball import SnowballStemmer
from nltk.stem.wordnet import WordNetLemmatizer

import unicodedata

def fix(s):
    u = s.decode('UTF-8')
    return unicodedata.normalize('NFKD', u).encode('ascii','ignore')



def tfidf_vectors():
    df = pd.read_csv('stlyrics_musical_tracks_url.csv')
    list_of_lyrics = df['track_lyrics'].dropna().tolist()

    clean_list_of_lyrics = ["".join([ch for ch in lyrics if ch not in punctuation])
                                    for lyrics in list_of_lyrics]

    snowball = SnowballStemmer('english')
    docs_snowball = [' '.join([snowball.stem(fix(word)) for word in lyrics.split()])
                     for lyrics in clean_list_of_lyrics]


    vectorizer = TfidfVectorizer(strip_accents='unicode', stop_words='english')
    tf_idf_vectors = vectorizer.fit_transform(docs_snowball) #scipy.sparse.csr.csr_matrix
    #words = vectorizer.get_feature_names()

    tfidf_array = tf_idf_vectors.toarray()

    return tfidf_array




def name_cleaner(composer):
    '''
    Returns a list of clean strings
    '''

    combo = composer.lower().replace(' and ', ',').split(',')
    clean_names = []
    for name in combo:
        for ch in punctuation:
            name = name.replace(ch, '')
        clean_names.append(name.strip())
    return clean_names


def name_list_mapper(list_of_names):
    lst = []
    for l in list_of_names:
        lst.extend(name_cleaner(l))

    unique_names = sorted(list(set(lst)))[1:]

    name_map = {name: i for i, name in enumerate(unique_names)}
    return name_map

