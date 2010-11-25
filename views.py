from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import render_to_response
from django.template import RequestContext, Template
from django.template.loader import get_template, render_to_string
from django.conf import settings
from models import *
from settings import *
from keys import *

import urllib
import pickle
import base64
import oauth2 as oauth
import oauthtwitter
import twitter

# Twitter Constants

def authorize(request):
    if request.user.is_authenticated() and ((not request.user.is_staff and ALLOW_NON_STAFF) or (request.user.is_staff and ALLOW_STAFF)):
        twitter_auth = oauthtwitter.OAuthApi(CONSUMER_KEY, CONSUMER_SECRET)
        if request.GET.has_key('oauth_token') or request.GET.has_key('oauth_verifier'):
            # Get temp_credentials from DB
            temp_credentials = {'oauth_token' : request.user.twitter.request_token,
                                'oauth_token_secret' : request.user.twitter.request_token_secret}
            # Get Access Token
            oauth_verifier = str(request.GET['oauth_verifier'])
            access_token = twitter_auth.getAccessToken(temp_credentials, oauth_verifier)
            # Save Data
            try: twitter_cred = request.user.twitter
            except: twitter_cred = TwitterAuth(user=request.user)
            twitter_cred.access_token = access_token['oauth_token']
            twitter_cred.access_token_secret = access_token['oauth_token_secret']
            twitter_cred.save()
            # Get User Data
            api = twitter.Api(consumer_key=CONSUMER_KEY,
                              consumer_secret=CONSUMER_SECRET,
                              access_token_key=twitter_cred.access_token,
                              access_token_secret=twitter_cred.access_token_secret)
            return HttpResponseRedirect(AUTH_REDIRECT)
        else:
            # Get the temporary credentials for our next few calls
            temp_credentials = twitter_auth.getRequestToken(callback=CALLBACK_URL)
            # Save temp_credentials in DB
            try: twitter_cred = request.user.twitter
            except: twitter_cred = TwitterAuth(user=request.user)
            twitter_cred.request_token = temp_credentials['oauth_token']
            twitter_cred.request_token_secret = temp_credentials['oauth_token_secret']
            twitter_cred.save()
            # Redirect User to Twitter
            return HttpResponseRedirect(twitter_auth.getAuthorizationURL(temp_credentials))
    elif (not request.user.is_staff and not ALLOW_NON_STAFF):
        return HttpResponse("Non Staff isn't allowed to do this.")
    elif (request.user.is_staff and not ALLOW_STAFF):
        return HttpResponse("Staff isn't allowed to do this.")
    else:
        return HttpResponse('Please Login first')
