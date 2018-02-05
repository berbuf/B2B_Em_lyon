"""
functions utilities for notebook simple Env
"""

import Preprocessing
import json
import numpy as np

path = "../data/indexed_tweets.json"
raw_data = json.load(open(path))
DATA = json.loads(raw_data)

COMPANY = ""
TWEETS = []

def get_tw(name, list_tw):
    """ get real tweets from preprocssed tweets """
    global COMPANY
    global TWEETS
    if not isinstance(list_tw[0], list):
        list_tw = [list_tw]
    if name != COMPANY:
        COMPANY = name
        request = "SELECT * FROM tweet WHERE searchterm = '@" + COMPANY + "'"
        TWEETS = np.array(Preprocessing.execute(request))[:,2]
    tw = next(e for e in DATA if e[0] == name)[2]
    return [ TWEETS[el[0]] for el in tw if el[1] in list_tw ]

def get_data(name):
    """ get preprocessed data """
    return list(map(lambda x: x[1], next(e for e in DATA if e[0] == name)[2]))

def get_tw_by_wd(company, word):
    """ return list of tweets with word"""
    data = get_data(company)
    return get_tw(company, [ e for e in data if word in e])
