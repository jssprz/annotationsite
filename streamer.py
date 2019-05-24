"""Defines TwitterStreamer class that inherits TwythonStreamer
"""

import os
import sys
import csv
import urllib3
import time
from twython import TwythonStreamer
from argparse import ArgumentParser
from configuration import ConfigurationFile

# sys.path.append('annotationsite')
os.environ['DJANGO_SETTINGS_MODULE'] = 'annotationsite.settings'
import django
django.setup()

from tweets.models import Tweet, TweetMedia, TweetUser, TweetHashTag

__author__ = "jssprz"
__version__ = "0.0.1"
__maintainer__ = "jssprz"
__email__ = "jperezmartin90@gmail.com"
__status__ = "Development"


class TwitterStreamer(TwythonStreamer):
    """
    """

    def __init__(self, customer_key, customer_secret, access_token, access_secret, save_media_dir):
        super(TwitterStreamer, self).__init__(customer_key, customer_secret, access_token, access_secret)

        self.__save_media_dir = save_media_dir

        # with open(r'saved_tweets.csv', 'w') as csvfile:
        #     fieldnames = ['hashtags', 'text', 'user', 'location', 'media_urls', 'saved_media_urls']
        #     writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        #     writer.writeheader()

    def on_success(self, data):
        """

        :param data: received data
        :param process_tweet_fn: function to process the data
        :return:
        """
        # Only collect tweets in English
        if self.filter_tweet(data):
            # tweet_data = self.process_tweet(data)
            self.save_to_model(data)

    # Problem with the API
    def on_error(self, status_code, data):
        print(status_code, data)
        self.disconnect()

    # Save each tweet to csv file
    def save_to_csv(self, tweet):
        with open(r'saved_tweets.csv', 'a', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(list(tweet.values()))
            print('tweet saved')

    def save_to_model(self, tweet):
        """

        :param tweet:
        :return:
        """

        if not Tweet.objects.filter(id_str=tweet['id_str']).exists():
            # get hashtag objects
            hashtags_texts = [hashtag['text'] for hashtag in tweet['entities']['hashtags']]
            hashtags_objs = []
            for h in hashtags_texts:
                if not TweetHashTag.objects.filter(text=h).exists():
                    h_obj = TweetHashTag(text=h)
                else:
                    h_obj = TweetHashTag.objects.get(text=h)
                h_obj.save()
                hashtags_objs.append(h_obj)

            # get user object
            if not TweetUser.objects.filter(id_str=tweet['user']['id_str']).exists():
                user_data = tweet['user']
                user_obj = TweetUser(id_str=user_data['id_str'], name=user_data['name'],
                                     screen_name=user_data['screen_name'], location=user_data['location'],
                                     url=user_data['url'])
                user_obj.save()
            else:
                user_obj = TweetUser.objects.get(pk=tweet['user']['id_str'])

            if tweet['coordinates'] is not None:
                coordinates_long = tweet['coordinates']['coordinates'][0]
                coordinates_lat = tweet['coordinates']['coordinates'][1]
            else:
                coordinates_long = None
                coordinates_lat = None

            ts = time.strftime('%Y-%m-%d %H:%M:%S',
                               time.strptime(tweet['created_at'], '%a %b %d %H:%M:%S +0000 %Y'))

            tweet_obj = Tweet(id_str=tweet['id_str'], text=tweet['text'], created_at=ts,
                              favorite_count=tweet['favorite_count'], retweet_count=tweet['retweet_count'],
                              coordinates_long=coordinates_long, coordinates_lat=coordinates_lat, lang=tweet['lang'],
                              user=user_obj, location=user_obj.location)

            medias = tweet['entities']['media']
            media_objs = []
            for i, m in enumerate(medias):
                # create or get the media object
                if not TweetMedia.objects.filter(id_str=m['id_str']).exists():
                    media_obj = TweetMedia(id_str=m['id_str'], url=m['url'], media_url=m['media_url'],
                                           media_url_https=m['media_url_https'], type=m['type'])
                    # download media
                    media_obj.cache()
                    print('media downloaded from: {}'.format(m['media_url']))
                else:
                    media_obj = TweetMedia.objects.get(id_str=m['id_str'])
                    print('media {} reused'.format(m['id_str']))

                media_obj.save()
                media_objs.append(media_obj)

            tweet_obj.save()
            tweet_obj.hashtags.set(hashtags_objs)
            tweet_obj.medias.set(media_objs)
            print('tweet saved')

        else:
            print('duplicated tweet')

    def filter_tweet(self, tweet):
        """

        :param tweet:
        :return:
        """

        return 'media' in tweet['entities']

    def process_tweet(self, tweet):
        """

        :param tweet:
        :return:
        """
        return {
            'hashtags': [hashtag['text'].encode("utf-8") for hashtag in tweet['entities']['hashtags']],
            'text': tweet['text'].encode("utf-8"),
            'user': tweet['user']['screen_name'].encode("utf-8"),
            'location': tweet['user']['location'],
            'media_urls': [media['media_url'] for media in
                           (tweet['entities']['media'] if 'media' in tweet['entities'] else [])]
        }

    def save_medias(self, tweet):
        media_urls = [media['media_url'] for media in
                      (tweet['entities']['media'] if 'media' in tweet['entities'] else [])]
        saved_paths = []
        http = urllib3.PoolManager()
        for i, url in enumerate(media_urls):
            r = http.request('GET', url, preload_content=False)

            path = os.path.abspath(
                os.path.join(self.__save_media_dir, '{}_{}.{}'.format(tweet['id_str'], i, url.split('.')[-1])))

            with open(path, 'wb') as out:
                while True:
                    data = r.read()
                    if not data:
                        break
                    out.write(data)
                    saved_paths.append(path)
        r.release_conn()
        return saved_paths


if __name__ == '__main__':
    parser = ArgumentParser('Crawling Twitter')
    parser.add_argument("-mode", type=str, choices=['request', 'streaming'],
                        help=" request | streaming ", required=True)
    parser.add_argument("-config", type=str, default='config.ini', help="a configuration file",
                        required=True)

    pargs = parser.parse_args()

    config = ConfigurationFile(pargs.config)

    if pargs.mode == 'streaming':
        stream = TwitterStreamer(config.twitter_consumer_key, config.twitter_consumer_secret,
                                 config.twitter_access_token, config.twitter_access_secret,
                                 config.path_to_save_media_dir)

        while True:
            try:
                # Start the stream
                stream.statuses.filter(track=config.query_track, follow=config.query_follow,
                                       locations=config.query_locations, delimited=config.query_delimited,
                                       stall_warnings=config.query_stall_warnings)
            except ConnectionResetError as re:
                print(re)
