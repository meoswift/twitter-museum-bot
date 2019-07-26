import tweepy
from tweepy import *
import random
from time import sleep
import requests
import os

KEYWORD = ['museum', 'museum preservation', 'art museum', 'museum exhibition', 'art reservation']
HAPPY_KEYWORD = ['amazing', 'happy', 'good', 'interesting', 'great', 'exciting', 'encouraged', 'fascinating',
                 'fascinated', 'love', 'joy', 'great', 'delighted', 'delight']
HAPPY_REPLY = ['Amazing!', 'This makes my day', 'Such a great job!', 'Absolutely awesome.', 'Cool stuff!',
               'Really like this :)' 'Everyone NEEDS to check this out!',
               'Museums are the best place on Earth.', 'Education is better with the existence of museums!',
               'I love this', 'Super cool project!!', 'A worthy read.', 'So glad I came across this!',
               'Wow!', 'Speechless with this']

# Twitter API
CONSUMER_KEY = 'HJ9nzMAXWQkzvA7g2lnqCvtDk'
CONSUMER_SECRET = 'yY07NWF9JctWxl8NDvUc6BE0cJnBGUhaOJmyQmBxDiXELb3l54'
ACCESS_KEY = '1137386491766759430-WIy1PMjAGrxc0Apeq13yLrFDv2WcKD'
ACCESS_SECRET = 'hpyW9naJztHoRRYt8g17uB3Rw631h4iA02exfWq2sq5tx'

auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
auth.set_access_token(ACCESS_KEY, ACCESS_SECRET)
api = tweepy.API(auth)

# Computer Vision API
SUBSCRIPTION_KEY = "18bdbe3fd8354591947ad37f9b489d10"

VISION_BASE_URL = "https://eastus.api.cognitive.microsoft.com/vision/v2.0/"
ANALYZE_URL = VISION_BASE_URL + "describe"

SUBREDDIT = 'https://www.reddit.com/r/ArchitecturePorn/.json?limit=50'


# scrape a list of image url from subreddit thread
def get_url_list():
    response = requests.get(SUBREDDIT, headers={'User-agent': 'your-bot-name 0.1'})
    if not response.ok:
        print("Error", response.status_code)
        exit()

    data = response.json()['data']['children']
    for post in data:
        url = post['data']['url']
        image_url_list.append(url)


# follow museums
def follow():
    key_index = random.randint(0, len(KEYWORD) - 1)
    users = api.search_users(q=KEYWORD[key_index], count=5, page=1)
    try:
        for user in users:
            api.create_friendship(user.id)
            sleep(50)
    except tweepy.TweepError as e:
        print(e)


# tweet with image and caption
def tweet_with_media():
    random_index = random.randint(0, len(image_url_list))

    url = image_url_list[random_index]
    print(url)
    message = print_caption(SUBSCRIPTION_KEY, ANALYZE_URL, url)

    filename = url.split('/')[-1]
    request = requests.get(url, stream=True)
    if request.status_code == 200:
        with open(filename, 'wb') as image:
            for chunk in request:
                image.write(chunk)

        api.update_with_media(filename, status=message)
        os.remove(filename)
    else:
        print("Unable to download image")


def print_caption(subscription_key, analyze_url, image_url):
    headers = {'Ocp-Apim-Subscription-Key': subscription_key}
    params = {'maxCandidates': '1', 'language': 'en'}
    content = {'url': image_url}
    try:
        response = requests.post(analyze_url, headers=headers, params=params, json=content)
        response.raise_for_status()
        analysis = response.json()
        try:
            image_caption = analysis["description"]["captions"][0]['text'].capitalize()
            return image_caption
        except BaseException as e:
            print(e)
    except requests.exceptions.HTTPError:
        pass


# only retweet
def retweet_only():
    print('only rt')
    random_index = random.randint(0, 100)
    if random_index % 2 == 0:
        retweet_from_search()
    else:
        retweet_from_timeline()


# retweet with a comment
def retweet_with_comment():
    print('inside comment')
    timeline_tweets = api.home_timeline(count=20, page=2)
    for tweet in timeline_tweets:
        print(tweet.favorite_count)  # debugging purposes
        print(tweet.retweeted)
        try:
            reply_index = random.randint(0, len(HAPPY_REPLY) - 1)
            user_displayname = tweet.user.screen_name
            if not tweet.retweeted and tweet.favorite_count >= 200 and user_displayname != 'museumistic':
                reply_status = HAPPY_REPLY[reply_index] + 'https://twitter.com/' + user_displayname + '/status/' \
                               + tweet.id_str
                api.update_status(status=reply_status)
                print('tweet updated')

        except tweepy.TweepError as e:
            print(e)


# retweet from search
def retweet_from_search():
    print('inside search')
    key_index = random.randint(0, len(KEYWORD) - 1)
    tweets = api.search(q=KEYWORD[key_index], count=50)
    for tweet in tweets:
        print(tweet.favorite_count)  # debugging purposes
        print(tweet.retweeted)
        try:
            if not tweet.retweeted and tweet.favorite_count >= 100:
                if not tweet.favorited:
                    api.create_favorite(tweet.id)
                    api.retweet(tweet.id)
                    print('retweeted')

        except tweepy.TweepError as e:
            print(e)


# retweet from timeline
def retweet_from_timeline():
    print('inside timeline')
    timeline_tweets = api.home_timeline(count=30)
    for tweet in timeline_tweets:
        print(tweet.favorite_count)  # debugging purposes
        print(tweet.retweeted)
        try:
            user_displayname = tweet.user.screen_name
            if not tweet.favorited and user_displayname != 'museumistic':
                api.create_favorite(tweet.id)
            if not tweet.retweeted and tweet.favorite_count > 100:
                api.retweet(tweet.id)
                print('retweeted')

        except tweepy.TweepError as e:
            print(e)


def main():
    get_url_list()
    while True:
        tweet_with_media()
        print('finished media tweet')
        follow()
        print('finished follow')
        retweet_only()
        retweet_with_comment()
        sleep(30)


if __name__ == "__main__":
    image_url_list = []
    main()
