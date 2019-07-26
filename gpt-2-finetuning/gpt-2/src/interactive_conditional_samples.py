#!/usr/bin/env python3

import fire
import json
import os
import numpy as np
import tensorflow as tf
import tweepy
from tweepy import *
import random
from newsapi.newsapi_client import NewsApiClient

import model, sample, encoder

# tweeting KEYWORDS
KEYWORDS = ['#Museum', '#Art Preservation', 'Historical architecture', '#Architecture', 'Modern art',
            'Museum conservation', 'Architects', 'Art museums', 'Historical buildings', 'City architecture',
            'Museum architects', 'Museum artifacts', 'Rural architecture']

# Twitter API
CONSUMER_KEY = 'HJ9nzMAXWQkzvA7g2lnqCvtDk'
CONSUMER_SECRET = 'yY07NWF9JctWxl8NDvUc6BE0cJnBGUhaOJmyQmBxDiXELb3l54'
ACCESS_KEY = '1137386491766759430-WIy1PMjAGrxc0Apeq13yLrFDv2WcKD'
ACCESS_SECRET = 'hpyW9naJztHoRRYt8g17uB3Rw631h4iA02exfWq2sq5tx'

auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
auth.set_access_token(ACCESS_KEY, ACCESS_SECRET)
api = tweepy.API(auth)

# News API
news_api = NewsApiClient(api_key='2152b1abf9bf489e946a24a24bcab732')


def get_headlines():
    headlines = news_api.get_everything(q='architecture, museum, art', language='en')
    articles = headlines['articles']
    headlines_list = []
    for article in articles:
        headline = article['description']
        headlines_list.append(headline)
        print(headline)
        print("-" * 80)


def interact_model(
        model_name='117M',
        seed=None,
        nsamples=1,
        batch_size=1,
        length=50,
        temperature=0.8,
        top_k=40,
        top_p=0.0):
    if batch_size is None:
        batch_size = 1
    assert nsamples % batch_size == 0

    enc = encoder.get_encoder(model_name)
    hparams = model.default_hparams()
    with open(os.path.join('models', model_name, 'hparams.json')) as f:
        hparams.override_from_dict(json.load(f))

    if length is None:
        length = hparams.n_ctx // 2
    elif length > hparams.n_ctx:
        raise ValueError("Can't get samples longer than window size: %s" % hparams.n_ctx)

    with tf.compat.v1.Session(graph=tf.Graph()) as sess:
        context = tf.compat.v1.placeholder(tf.int32, [batch_size, None])
        np.random.seed(seed)
        tf.compat.v1.set_random_seed(seed)
        output = sample.sample_sequence(
            hparams=hparams, length=length,
            context=context,
            batch_size=batch_size,
            temperature=temperature, top_k=top_k, top_p=top_p
        )

        saver = tf.compat.v1.train.Saver()
        ckpt = tf.train.latest_checkpoint(os.path.join('models', model_name))
        saver.restore(sess, ckpt)

        while True:
            key_index = random.randint(0, len(KEYWORDS) - 1)
            raw_text = KEYWORDS[key_index]
            '''
            raw_text = input("Model prompt >>> ")
            while not raw_text:
                print('Prompt should not be empty!')
                raw_text = input("Model prompt >>> ")
            '''
            context_tokens = enc.encode(raw_text)
            for _ in range(nsamples // batch_size):
                out = sess.run(output, feed_dict={
                    context: [context_tokens for _ in range(batch_size)]
                })[:, len(context_tokens):]
                for i in range(batch_size):
                    response = enc.decode(out[i])
                    final_text = raw_text + response + ' ...'
                    return final_text


def update_status(tweet):
    try:
        api.update_status(status=tweet)
        print('tweeted')
    except tweepy.TweepError as e:
        print(e)


if __name__ == '__main__':
    # text = fire.Fire(interact_model)
    # update_status(text)
    get_headlines()
