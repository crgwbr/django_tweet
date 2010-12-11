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
import oauthfacebook
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
        twitter_auth = oauthtwitter.OAuthApi(TWITTER_CONSUMER_KEY, TWITTER_CONSUMER_SECRET)
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
            # Verify User Auth
            api = twitter.Api(consumer_key=TWITTER_CONSUMER_KEY,
                              consumer_secret=TWITTER_CONSUMER_SECRET,
                              access_token_key=twitter_cred.access_token,
                              access_token_secret=twitter_cred.access_token_secret)
            profile = api.VerifyCredentials()
            twitter_cred.uid = profile.id
            twitter_cred.save()
            return HttpResponseRedirect(AUTH_REDIRECT)
        else:
            # Get the temporary credentials for our next few calls
            temp_credentials = twitter_auth.getRequestToken(callback=ADD_TWITTER_URL)
            # Save temp_credentials in DB
            try: twitter_cred = request.user.twitter
            except: twitter_cred = TwitterAuth(user=request.user)
            twitter_cred.request_token = temp_credentials['oauth_token']
            twitter_cred.request_token_secret = temp_credentials['oauth_token_secret']
            twitter_cred.save()
            # Redirect User to Twitter
            return HttpResponseRedirect(twitter_auth.getAuthorizationURL(temp_credentials))
    elif (not request.user.is_staff and not ALLOW_NON_STAFF):
        # Non staff isn't allowed to do this
        url = "?".join((AUTH_DENIED, 'message=Non-staff%20isn\'t%20allowed%20to%20do%20this.'))
        return HttpResponseRedirect(url)
    elif (request.user.is_staff and not ALLOW_STAFF):
        # Staff isn't allowed to do this
        url = "?".join((AUTH_DENIED, 'message=Staff%20isn\'t%20allowed%20to%20do%20this.'))
        return HttpResponseRedirect(url)
    else:
        return HttpResponseRedirect(TWITTER_LOGIN_URL)

"""
===========================================================================================================================================
Implements Login with Twitter
Does both Login and create new user (if nessasary)
"""
def login_with_twitter(request):
    twitter_auth = oauthtwitter.OAuthApi(TWITTER_CONSUMER_KEY, TWITTER_CONSUMER_SECRET)
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
        api = twitter.Api(consumer_key=TWITTER_CONSUMER_KEY,
                          consumer_secret=TWITTER_CONSUMER_SECRET,
                          access_token_key=access_token,
                          access_token_secret=access_token_secret)
        profile = api.VerifyCredentials()
        # Login User
        user = authenticate(profile = profile,
                            access_token = access_token,
                            access_token_secret = access_token_secret,
                            twitter = True)
        
        if user != None:
            login(request, user)
        else:
            url = "?".join((AUTH_DENIED, 'message=Unexpected%20Auth%20Error'))
            return HttpResponseRedirect(url)
        # Redirect user
        url = request.session.get('redirect', AUTH_REDIRECT)
        if request.session.has_key('redirect'): del request.session['redirect']
        return HttpResponseRedirect(url)
    else:
        # Get the temporary credentials for our next few calls
        temp_credentials = twitter_auth.getRequestToken(callback=TWITTER_LOGIN_URL)
        # Save temp_credentials
        request.session['request_token'] = temp_credentials['oauth_token']
        request.session['request_token_secret'] = temp_credentials['oauth_token_secret']
        request.session.modified = True
        # Set login redirect
        if request.GET.has_key('redirect'):
            request.session['redirect'] = request.GET['redirect']
        # Redirect User to Twitter
        return HttpResponseRedirect(twitter_auth.getAuthorizationURL(temp_credentials, url=TWITTER_AUTHENTICATE_URL))

"""
===========================================================================================================================================
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
            return HttpResponseRedirect('%s?redirect=%s' % (TWITTER_LOGIN_URL, request.META.get('HTTP_REFERER', AUTH_REDIRECT)))
    return HttpResponseRedirect(request.META.get('HTTP_REFERER', AUTH_REDIRECT))

"""
===========================================================================================================================================
Testing Only
Don't use this
"""
def tweet_form(request):
    if request.user.is_authenticated():
        # Get user Data
        user = request.user.twitter.get_profile_data()
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



"""
===========================================================================================================================================
Facebook Views Start Here
===========================================================================================================================================

Authorize with facebook
"""
def authorize_with_facebook(request):
    if request.user.is_authenticated() and ((not request.user.is_staff and ALLOW_NON_STAFF) or (request.user.is_staff and ALLOW_STAFF)):
        facebook = oauthfacebook.OAuthAPI(FACEBOOK_APP_ID, FACEBOOK_APP_SECRET)
        verification_code = request.GET.get("code", None)
        if verification_code:
            access_token = facebook.getAccessToken(verification_code, 'http://%s/%s/add_facebook' % (settings.TARGET_HOST, APP_URL_PREFIX))
            # Save Data
            try: facebook_cred = request.user.facebook
            except: facebook_cred = FacebookAuth(user=request.user)
            facebook_cred.access_token = access_token
            facebook_cred.refresh_profile_data()
            facebook_cred.uid = facebook_cred.get_profile_data()['id']
            facebook_cred.save()
            return HttpResponseRedirect(AUTH_REDIRECT)
        else:
            return HttpResponseRedirect(facebook.getAuthorizationURL(ADD_FACEBOOK_URL))
    elif (not request.user.is_staff and not ALLOW_NON_STAFF):
        # Non staff isn't allowed to do this
        url = "?".join((AUTH_DENIED, 'message=Non-staff%20isn\'t%20allowed%20to%20do%20this.'))
        return HttpResponseRedirect(url)
    elif (request.user.is_staff and not ALLOW_STAFF):
        # Staff isn't allowed to do this
        url = "?".join((AUTH_DENIED, 'message=Staff%20isn\'t%20allowed%20to%20do%20this.'))
        return HttpResponseRedirect(url)
    else:
        return HttpResponseRedirect(FACEBOOK_LOGIN_URL)

"""
===========================================================================================================================================
Implements Login with Facebook
Does both Login and create new user (if nessasary)
"""
def login_with_facebook(request):
    facebook = oauthfacebook.OAuthAPI(FACEBOOK_APP_ID, FACEBOOK_APP_SECRET)
    verification_code = request.GET.get("code", None)
    if verification_code:
        access_token = facebook.getAccessToken(verification_code, FACEBOOK_LOGIN_URL)
        profile = facebook.getProfile()
        # Login User
        user = authenticate(profile = profile,
                            access_token = access_token,
                            facebook = True)
        if user != None:
            login(request, user)
        else:
            url = "?".join((AUTH_DENIED, 'message=Unexpected%20Auth%20Error'))
            return HttpResponseRedirect(url)
        # Redirect user
        url = request.session.get('redirect', AUTH_REDIRECT)
        if request.session.has_key('redirect'): del request.session['redirect']
        return HttpResponseRedirect(url)
    else:
        # Set login redirect
        if request.GET.has_key('redirect'):
            request.session['redirect'] = request.GET['redirect']
        # Redirect
        return HttpResponseRedirect(facebook.getAuthorizationURL(FACEBOOK_LOGIN_URL))

















    
