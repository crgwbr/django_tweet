# Django Social Auth Backend

from django.conf import settings
from django.contrib.auth.models import User
from models import *


class TwitterBackend:
    # Auth for Twitter Login
    # Returns a user if one exists
    # Creates on if it doesn't exist already
    def authenticate(self, profile=None, access_token=None, access_token_secret=None, twitter=False):
        if not twitter:
            return None
        try:
            user = User.objects.get(twitter__uid = profile.id)
            if user.twitter.access_token_secret == access_token_secret:
                return user
            else:
                return None
        except User.DoesNotExist:
            user = User.objects.create_user('%s@twitter' % profile.id, '')
            if " " in profile.name:
                user.first_name = profile.name.split(' ')[0]
                user.last_name = profile.name.split(' ')[1]
            else:
                user.first_name = profile.name
            user.is_active = True
            user.save()
            # Save Twitter Data
            twitter_cred = TwitterAuth(user=user)
            twitter_cred.access_token = access_token
            twitter_cred.access_token_secret = access_token_secret
            twitter_cred.refresh_profile_data()
            twitter_cred.uid = twitter_cred.get_profile_data().id
            twitter_cred.save()
            return user

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None


class FacebookBackend:
    # Auth for Twitter Login
    # Returns a user if one exists
    # Creates on if it doesn't exist already
    def authenticate(self, profile=None, access_token=None, facebook=False):
        if not facebook:
            return None
        try:
            user = User.objects.get(facebook__uid = profile['id'])
            if user.facebook.access_token == access_token:
                return user
            else:
                return None
        except User.DoesNotExist:
            user = User.objects.create_user('%s@facebook' % profile['id'], '')
            user.first_name = profile['first_name']
            user.last_name = profile['last_name']
            user.email_address = profile.get('email', '')
            user.is_active = True
            user.save()
            # Save Twitter Data
            facebook_cred = FacebookAuth(user=user)
            facebook_cred.access_token = access_token
            facebook_cred.refresh_profile_data()
            facebook_cred.uid = facebook_cred.get_profile_data()['id']
            facebook_cred.save()
            return user

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
