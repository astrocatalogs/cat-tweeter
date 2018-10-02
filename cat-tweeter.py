"""Tweet out a weekly summary of the most popular OAC objects."""
import json
import sys
import time
import urllib

import tweepy

month_tweet = len(sys.argv) > 1 and sys.argv[1] == 'month'

nicename = {
    "sne": "supernova",
    "tde": "tidal disruption",
    "kilonova": "kilonova",
    "hvs": "fast star"
}

emojis = {
    "sne": "💥",
    "tde": "💫⚫️",
    "kilonova": "💞",
    "faststars": "⭐️💨"
}

with open('twitter-api.json', 'r') as f:
    twit = json.load(f)

auth = tweepy.OAuthHandler(twit['consumer_key'], twit['consumer_secret'])
auth.set_access_token(twit['access_token'], twit['access_token_secret'])
api = tweepy.API(auth)

# Retrieve the top 5 objects.
count_url = 'http://astrocats.space/api-count.php'
if month_tweet:
    count_url += '?month'
response = urllib.request.urlopen(count_url)
respj = json.loads(response.read().decode('utf-8'))

objects = [x.strip() for x in respj['top5'].split(',')]

# Which catalog are these objects from?
response = urllib.request.urlopen(
    'https://api.astrocats.space/{}/claimedtype+catalog'.format(
        '+'.join(objects)))
respj = json.loads(response.read().decode('utf-8'))

print(respj)

cats = [respj[x]['catalog'][0] for x in respj]
nicecats = [nicename.get(x, '') for x in cats]

print(cats)

types = [respj[x].get('claimedtype', [{'value': ''}])[
    0].get('value', '') for x in respj]

obj_count = 5
while True:
    try:
        if month_tweet:
            tweet_txt = (
                "Most requested objects "
                "for {}:\n\n".format(
                    time.strftime("%B %Y")))
        else:
            tweet_txt = (
                "Most requested objects "
                "for week of {}:\n\n").format(
                    time.strftime("%B") + " " +
                    time.strftime("%d, %Y").lstrip("0"))

        for oi, obj in enumerate(objects[:obj_count]):
            type_cat = types[oi] + ' ' + nicecats[oi] if (
                types[oi] != '' and types[oi].lower() != nicecats[
                    oi].lower()) else nicecats[oi].capitalize()
            tweet_txt += '{} {}, {} http://{}.space/{}/{}'.format(
                emojis[cats[oi]], obj, type_cat,
                cats[oi], cats[oi], obj)
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
