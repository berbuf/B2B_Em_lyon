
"""
preprocessing utility
"""

from wordcloud import WordCloud
import matplotlib.pyplot as plt
from gensim.models import Phrases
from gensim.models.phrases import Phraser
from langdetect import detect
import mysql.connector
import numpy as np
import collections
import json
import re

CNX = mysql.connector.connect(user="emlyon1",
                              password="student1",
                              host="analyst-toolbelt.cn119w37trlg.eu-west-1.rds.amazonaws.com",
                              database="B2B")

path = "../data/lang_id.json"
raw_data = json.load(open(path))
LANG_IDS = json.loads(raw_data)

def execute(sql_query):
    """ execute sql query and return python list """
    cursor = CNX.cursor()
    cursor.execute(sql_query)
    return list(cursor)

def mark_bigrams(tweets):
    """ join bigrams with '_' """ 
    bigram = Phrases(tweets)
    bigram_phraser = Phraser(bigram)
    return list(bigram_phraser[tweets])

def preprocessing(company, lang):
    """
    take company name, language chosen
    return meta-data and list of preprocessed tweets
    """

    # get tweets
    tweets = np.array(execute("SELECT * FROM tweet WHERE searchterm = '@" + company + "'"))
    tweets = tweets[:,2]

    # count retweets
    pattern = re.compile("^RT ")
    rt_tweets = [ tweet for tweet in tweets if pattern.match(tweet) ]

    # only lang tweets
    lang_tweets = []
    for tweet in rt_tweets:
        try:
            if detect(tweet) == lang:
                lang_tweets.append(tweet)
        except:
            continue

    # no urls
    url = 'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
    no_url_tweets = [ re.sub(url, '', tweet) for tweet in lang_tweets ]

    # remove @ words
    no_arobas_tweets = [ re.sub(r"([@?]\w+)\b", '', text) for text in no_url_tweets ]

    # remove non-alphanumerical characters
    only_alphanum_tweets = [ re.sub(r'[^\w]', ' ', text) for text in no_arobas_tweets ]

    # tokenizing
    tokenized_tweets = [ tweet.split(" ") for tweet in only_alphanum_tweets ]

    # lower tweets and remove one char words
    lowered_tweets = [ [ word.lower() for word in text if len(word) > 1 ] for text in tokenized_tweets ]
    
    # remove stopwords
    stopwords = open("./stopwords").read().split("\n")
    stopwords += ["mon", "tue", "wed", "thu", "fri", "sat", "sun", 
                  "jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec",
                  "amp", "rt", "https"]
    filtered_tweets = [ [ word for word in text if word not in stopwords ] for text in lowered_tweets ]

    # isolate bigrams
    bigrams = mark_bigrams(filtered_tweets)

    # reduce to one list of words
    flat_text_bigrams = [ word for tweet in bigrams for word in tweet ]
    flat_text = [ word for tweet in filtered_tweets for word in tweet ]

    # get frequency dictionary
    frequ = collections.Counter(flat_text_bigrams).most_common()

    # return format
    # * name company
    # * number tweets
    # * nb retweet
    # * language chosen
    # * nb tweet in chosen language
    # * nb words
    # * nb unique words
    data = (company, len(tweets), len(rt_tweets), lang, len(lang_tweets), len(flat_text_bigrams), len(frequ), filtered_tweets)

    return data

def fast_preprocessing(company, lang, no_arobas=True, no_rt=True):
    """
    take company name, language chosen, id by language list
    fast preprocessing using prebuild lang_ids
    """

    # get tweets
    tweets = np.array(execute("SELECT * FROM tweet WHERE searchterm = '@" + company + "'"))
    tweets = tweets[:,2]

    # get only tweets of lang language
    lang_id = next(e for e in LANG_IDS if e[0] == company)[1]
    lang_tweets = [ (elem[0], tweets[elem[0]]) for elem in lang_id if elem[1] == lang ]

    # remove retweets
    if no_rt:
        pattern = re.compile("^RT ")
        no_rt_tweets = [ (i, tweet) for i, tweet in lang_tweets if not pattern.match(tweet) ]
    else:
        no_rt_tweets = lang_tweets

    # no urls
    url = 'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
    no_url_tweets = [ (i, re.sub(url, '', tweet)) for i, tweet in no_rt_tweets ]

    if no_arobas:
        # remove @ words
        no_arobas_tweets = [ (i, re.sub(r"([@?]\w+)\b", '', text)) for i, text in no_url_tweets ]
    else:
        no_arobas_tweets = no_url_tweets

    # remove non-alphanumerical characters
    only_alphanum_tweets = [ (i, re.sub(r'[^\w]', ' ', text)) for i, text in no_arobas_tweets ]

    # tokenizing
    tokenized_tweets = [ (i, tweet.split(" ")) for i, tweet in only_alphanum_tweets ]

    # lower tweets and remove one char words
    lowered_tweets = [ (i, [ word.lower() for word in text if len(word) > 1 ]) for i, text in tokenized_tweets ]
    
    # remove stopwords
    stopwords = open("./stopwords").read().split("\n")
    stopwords += ["mon", "tue", "wed", "thu", "fri", "sat", "sun", 
                  "jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec",
                  "amp", "rt", "https"]
    filtered_tweets = [ (i, [ word for word in text if word not in stopwords ]) for i, text in lowered_tweets ]

    # format = name, language, tweets
    data = (company, lang, filtered_tweets)

    return data

def get_tweets_no_rt(company, lang):
    # get tweets
    tweets = np.array(execute("SELECT * FROM tweet WHERE searchterm = '@" + company + "'"))
    tweets = tweets[:,2]

    # get only tweets of lang language
    lang_id = next(e for e in LANG_IDS if e[0] == company)[1]
    lang_tweets = [ (elem[0], tweets[elem[0]]) for elem in lang_id if elem[1] == lang ]

    # remove retweets
    pattern = re.compile("^RT ")
    no_rt_tweets = [ (i, tweet) for i, tweet in lang_tweets if not pattern.match(tweet) ]

    return no_rt_tweets
