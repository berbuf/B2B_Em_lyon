import json
from gensim.models import Phrases
from gensim.models.phrases import Phraser

import numpy as np


def get_tweets(dataset_path):
    raw_data = json.load(open(dataset_path))
    data = json.loads(raw_data)
    return data

def train_and_save(dataset_path):
    data = get_tweets(dataset_path)

    tweets = []
    for c in data:
        _, _, _, _, _, _, _, c_tweets = c
        tweets.append(c_tweets)
    np_tweets = np.array(tweets)
    np_tweets = np.concatenate(np_tweets, 0)
    tweets = np_tweets.tolist()

    phrases = Phrases(tweets)
    bigram = Phraser(phrases)
    bigram.save("../models/bigram_model")

def load_model(path_to_file):
    bigram = Phraser.load(path_to_file)
    return bigram
