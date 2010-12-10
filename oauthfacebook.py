# Facebook OAuth implementation by Craig Weber
# Based on https://github.com/facebook/python-sdk/blob/master/examples/oauth/facebookoauth.py

import urllib
import cgi
from django.utils import simplejson as json

AUTHORIZE_URL = "https://graph.facebook.com/oauth/authorize"
ACCESS_TOKEN_URL = "https://graph.facebook.com/oauth/access_token"
PROFILE_URL = "https://graph.facebook.com/me"

class OAuthAPI:
    def __init__(self, app_id, app_secret):
        self.app_id = app_id
        self.app_secret = app_secret
        
    def getAuthorizationURL(self, redirect):
        args = {'client_id' : self.app_id,
                'redirect_uri' : redirect}
        return "?".join([AUTHORIZE_URL, urllib.urlencode(args)])

    def getAccessToken(self, code, redirect):
        args = {'client_id' : self.app_id,
                'redirect_uri' : redirect,
                'client_secret' : self.app_secret,
                'code' : code}
        url = "?".join([ACCESS_TOKEN_URL, urllib.urlencode(args)])
        response = urllib.urlopen(url).read()
        response = cgi.parse_qs(response)
        self.access_token = response["access_token"][-1]
        return self.access_token

    def getProfile(self, access_token=None):
        if not access_token:
            access_token = self.access_token
        url = "?".join([PROFILE_URL, urllib.urlencode(dict(access_token=access_token))])
        profile = json.load(urllib.urlopen(url))
        return profile
