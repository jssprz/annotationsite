#!/usr/bin/env python
"""
"""

from configparser import ConfigParser

__author__ = "jssprz"
__version__ = "0.0.1"
__maintainer__ = "jssprz"
__email__ = "jperezmartin90@gmail.com"
__status__ = "Development"


class ConfigurationFile:
    """
    """

    def __init__(self, config_path):
        self.__config = ConfigParser()
        self.__config.read(config_path)

        try:
            twitter_section = self.__config['TWITTER']
        except Exception:
            raise ValueError(" {} is not defined in the configuration file".format('TWITTER'))

        try:
            self.__consumer_key = twitter_section['CONSUMER_KEY']
            self.__consumer_secret = twitter_section['CONSUMER_SECRET']
            self.__access_token = twitter_section['ACCESS_TOKEN']
            self.__access_secret = twitter_section['ACCESS_SECRET']

            if 'QUERY' in self.__config.sections():
                query_section = self.__config['QUERY']
                self.__query_follow = query_section['FOLLOW']
                self.__query_track = query_section['TRACK']
                self.__query_locations = query_section['LOCATIONS']
                self.__query_delimited = query_section['DELIMITED']
                self.__query_stall_warnings = query_section['STALL_WARNINGS']

            if 'PATHS' in self.__config.sections():
                paths_section = self.__config['PATHS']
                self.__save_media_dir = paths_section['SAVE_MEDIA_DIR']

        except Exception:
            raise ValueError("something wrong with the parameters in the configuration file " + config_path)

    @property
    def twitter_consumer_key(self):
        return self.__consumer_key

    @property
    def twitter_consumer_secret(self):
        return self.__consumer_secret

    @property
    def twitter_access_token(self):
        return self.__access_token

    @property
    def twitter_access_secret(self):
        return self.__access_secret

    @property
    def query_track(self):
        return self.__query_track

    @property
    def query_follow(self):
        return self.__query_follow

    @property
    def query_locations(self):
        return self.__query_locations

    @property
    def query_delimited(self):
        return self.__query_delimited

    @property
    def query_stall_warnings(self):
        return self.__query_stall_warnings

    @property
    def path_to_save_media_dir(self):
        return self.__save_media_dir
