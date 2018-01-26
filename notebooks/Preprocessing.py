
"""
preprocessing utility
"""

from wordcloud import WordCloud
import matplotlib.pyplot as plt
from gensim.models import Phrases
from gensim.models.phrases import Phraser
from langdetect import detect
from TrainBigrams import load_model
import mysql.connector
import numpy as np
import collections
import re

cnx = mysql.connector.connect(user="emlyon1",
                              password="student1",
                              host="analyst-toolbelt.cn119w37trlg.eu-west-1.rds.amazonaws.com",
                              database="B2B")

def execute(sql_query):
    """ execute sql query and return python list """
    cursor = cnx.cursor()
    cursor.execute(sql_query)
    return list(cursor)

def mark_bigrams(tweets):
    """ join bigrams with '_' """ 
    bigram_phraser = load_model('../models/bigram_model')
    return list(bigram_phraser[tweets])

def preprocessing(company, lang, wordcloud=False):
    """
    take company name, language chosen, boolean for saving wordcloud 
    return meta-data and list of preprocessed tweets
    """

    # get tweets
    tweets = np.array(execute("SELECT * FROM tweet WHERE searchterm = '@" + company + "'"))
    tweets = tweets[:,2]

    # get retweets
    pattern = re.compile("^RT ")
    rt_tweets = [ tweet for tweet in tweets if pattern.match(tweet) ]

    # only lang tweets
    lang_tweets = []
    for tweet in tweets:
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

    # save wordcloud
    if wordcloud:
        wordcloud = WordCloud(width=1600, height=800, max_words=2000).generate(" ".join(flat_text))
        image = wordcloud.to_image()
        image.save("wordclouds/wordcloud_" + company + ".png")

    # return format
    # * name company
    # * number tweets
    # * nb retweet
    # * language chosen
    # * nb tweet in chosen language
    # * nb words
    # * nb unique words
    data = (company, len(tweets), len(rt_tweets), lang, len(lang_tweets), len(flat_text_bigrams), len(frequ), bigrams)

    return data
