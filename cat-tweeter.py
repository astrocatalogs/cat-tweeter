"""Tweet out a weekly summary of the most popular OAC objects."""
import json
import time
import urllib

import tweepy

nicename = {
    "sne": "supernova",
    "tde": "tidal disruption",
    "kne": "kilonova",
    "hvs": "fast star"
}

urls = {
    "sne": "sne",
    "tde": "tde",
    "kne": "kilonova",
    "hvs": "faststars"
}

emojis = {
    "sne": "💥",
    "tde": "💫⚫️",
    "kne": "💞",
    "hvs": "⭐️💨"
}

with open('twitter-api.json', 'r') as f:
    twit = json.load(f)

auth = tweepy.OAuthHandler(twit['consumer_key'], twit['consumer_secret'])
auth.set_access_token(twit['access_token'], twit['access_token_secret'])
api = tweepy.API(auth)

# Retrieve the top 5 objects.
response = urllib.request.urlopen('http://astrocats.space/api-count.php')
respj = json.loads(response.read().decode('utf-8'))

objects = [x.strip() for x in respj['top5'].split(',')]

# Which catalog are these objects from?
response = urllib.request.urlopen(
    'https://api.astrocats.space/{}/claimedtype+catalog'.format(
        '+'.join(objects)))
respj = json.loads(response.read().decode('utf-8'))

cats = [respj[x]['catalog'][0] for x in respj]
nicecats = [nicename.get(x, '') for x in cats]

types = [respj[x].get('claimedtype', [{'value': ''}])[
    0].get('value', '') for x in respj]
types = ['Type ' + x if x != '' else x for x in types]

obj_count = 5
while True:
    try:
        tweet_txt = (
            "Most requested objects "
            "for week of {}:\n\n").format(
                time.strftime("%B") + " " +
                time.strftime("%d, %Y").lstrip("0"))

        for oi, obj in enumerate(objects[:obj_count]):
            tweet_txt += '{} {}, {} {} http://{}.space/{}/{}'.format(
                emojis[cats[oi]], obj, types[oi], nicecats[oi],
                urls[cats[oi]], cats[oi], obj)
            if oi < obj_count - 1:
                tweet_txt += '\n'

        print(tweet_txt)

        api.update_status(tweet_txt)
        break
    except tweepy.error.TweepError:
        obj_count -= 1
        if obj_count <= 0:
            break
    except Exception:
        raise
