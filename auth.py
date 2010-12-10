# Django Social Auth Backend

from django.conf import settings
from django.contrib.auth.models import User
from models import *


class TwitterBackend:
    # Auth for Twitter Login
    # Returns a user if one exists
    # Creates on if it doesn't exist already
    def authenticate(self, profile=None, access_token=None, access_token_secret=None):
        try:
            user = User.objects.get(username= "%s@twitter" % profile.id )
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
            twitter_cred.save()
            return user

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
