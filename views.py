from django.contrib.auth import authenticate, login
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

"""
===========================================================================================================================================
Twitter Views Start Here
===========================================================================================================================================

Add Twitter Credentials to an existing user
User should be logged in
Creates a new account (via views.login_with_twitter) if request.user.is_authenticated == False
"""
def authorize_with_twitter(request):
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
            # Verify User Auth
            api = twitter.Api(consumer_key=CONSUMER_KEY,
                              consumer_secret=CONSUMER_SECRET,
                              access_token_key=twitter_cred.access_token,
                              access_token_secret=twitter_cred.access_token_secret)
            api.VerifyCredentials()
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
        return HttpResponseRedirect('/%s/register')

"""
Implements Login with Twitter
Does both Login and create new user (if nessasary)
"""
def login_with_twitter(request):
    twitter_auth = oauthtwitter.OAuthApi(CONSUMER_KEY, CONSUMER_SECRET)
    if request.GET.has_key('oauth_token') or request.GET.has_key('oauth_verifier'):
        # Get temp_credentials from DB
        temp_credentials = {'oauth_token' : request.session['request_token'],
                            'oauth_token_secret' : request.session['request_token_secret']}
        # Get Access Token
        oauth_verifier = str(request.GET['oauth_verifier'])
        token = twitter_auth.getAccessToken(temp_credentials, oauth_verifier)
        access_token = token['oauth_token']
        access_token_secret = token['oauth_token_secret']
        # Verify User Auth with Twitter
        api = twitter.Api(consumer_key=CONSUMER_KEY,
                          consumer_secret=CONSUMER_SECRET,
                          access_token_key=access_token,
                          access_token_secret=access_token_secret)
        profile = api.VerifyCredentials()
        # Login User
        user = authenticate(profile = profile,
                            access_token = access_token,
                            access_token_secret = access_token_secret)
        
        if user != None:
            login(request, user)
        else:
            raise Exception("Auth Error: %s %s" % ('%s@twitter' % profile.id, access_token_secret))
        # Redirect user
        return HttpResponseRedirect(request.session.get('redirect', AUTH_REDIRECT))
    else:
        # Get the temporary credentials for our next few calls
        temp_credentials = twitter_auth.getRequestToken(callback=REGISTER_URL)
        # Save temp_credentials
        request.session['request_token'] = temp_credentials['oauth_token']
        request.session['request_token_secret'] = temp_credentials['oauth_token_secret']
        request.session.modified = True
        # Set login redirect
        if request.GET.has_key('redirect'):
            request.session['redirect'] = request.GET['redirect']
        # Redirect User to Twitter
        return HttpResponseRedirect(twitter_auth.getAuthorizationURL(temp_credentials, url=AUTHENTICATE_URL))

"""
Sends a tweet as the logged in user
use this as the target of a POST form, returns to HTTP_REFERER after post
PostData: update=Tweet%20This
"""
def send_tweet(request):
    if request.method == 'POST' and request.POST.has_key('update'):
        if request.user.is_authenticated():
            # Send Tweet
            api = request.user.twitter.api()
            status = api.PostUpdate(request.POST['update'])
        else:
            # Log in user
            return HttpResponseRedirect('/%s/register?redirect=%s' % (APP_URL_PREFIX, request.META.get('HTTP_REFERER', AUTH_REDIRECT)))
    if request.META.has_key('HTTP_REFERER'):
        return HttpResponseRedirect(request.META['HTTP_REFERER'])
    else:
        return HttpResponseRedirect("/")

"""
Testing Only
Don't use this
"""
def tweet_form(request):
    if request.user.is_authenticated():
        # Get user Data
        api = request.user.twitter.api()
        user = api.VerifyCredentials()
        # Assemble and return Form
        temp = Template("""
        <img src="{{profile_image_url}}" /><br/>
        Logged in as {{name}}<br/>
        You have {{friends_count}} friends, {{followers_count}} followers, and {{statuses_count}} status updates.<br/>
        <form action="/twitter/post" method="post">{% csrf_token %}
        <textarea name="update">Type your update here</textarea><br/>
        <input type="submit" value="Post Tweet" />
        </form>
        """)
        context = RequestContext(request, user.AsDict())
        return HttpResponse(temp.render(context))
    return HttpResponseRedirect('/')



    
