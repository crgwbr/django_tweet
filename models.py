from django.db import models
from django.contrib.auth.models import User
from django.utils import simplejson as json

import pickle
from datetime import datetime

from keys import *
import twitter
import facebook
import urllib

class TwitterAuth(models.Model):
    user = models.OneToOneField(User, related_name='twitter')
    uid = models.CharField(max_length=200)
    
    request_token = models.TextField(null=True)
    request_token_secret = models.TextField(null=True)

    access_token = models.TextField(null=True)
    access_token_secret = models.TextField(null=True)
    
    profile_data = models.TextField(null=True)
    profile_refreshed = models.DateTimeField(null=True)

    def api(self):
        api = twitter.Api(consumer_key = TWITTER_CONSUMER_KEY,
                          consumer_secret = TWITTER_CONSUMER_SECRET,
                          access_token_key = self.access_token,
                          access_token_secret = self.access_token_secret)
        return api
    
    def get_profile_data(self):
        # Refreshes profile data if its older than 7 days
        # Returns unpickled profile data object
        delta = datetime.now() - self.profile_refreshed
        if delta.days > 7:
            self.refresh_profile_data()
        profile = pickle.loads(str(self.profile_data))
        return profile

    def refresh_profile_data(self):
        # Refreshes Cached Profile data
        # Profile data is cached to prevent overuse of Twitter's API
        api = self.api()
        profile = api.VerifyCredentials()
        self.profile_data = pickle.dumps(profile)
        self.profile_refreshed = datetime.now()
        self.save()

    def __unicode__(self):
        return self.uid


class FacebookAuth(models.Model):
    user = models.OneToOneField(User, related_name='facebook')
    uid = models.CharField(max_length=200)

    access_token = models.TextField(null=True)
    access_token_secret = models.TextField(null=True)
    
    profile_data = models.TextField(null=True)
    profile_refreshed = models.DateTimeField(null=True)

    def api(self):
        # Returns an instance of the Facebook GraphAPI for the user.
        # See https://github.com/facebook/python-sdk/blob/master/src/facebook.py
        api = facebook.GraphAPI(access_token=self.access_token)
        return api

    def get_profile_data(self):
        # Refreshes profile data if its older than 7 days
        # Returns unpickled profile data object
        delta = datetime.now() - self.profile_refreshed
        if delta.days > 7:
            self.refresh_profile_data()
        profile = pickle.loads(str(self.profile_data))
        return profile

    def refresh_profile_data(self):
        # Refreshes Cached Profile data
        # Profile data is cached to prevent overuse of API
        graph = self.api()
        profile = graph.get_object('me')
        self.profile_data = pickle.dumps(profile)
        self.profile_refreshed = datetime.now()
        self.save()

    def __unicode__(self):
        return self.uid
