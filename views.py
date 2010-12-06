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
        return HttpResponse('Please Login first')

def new_user(request):
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
        # Verify User Auth
        api = twitter.Api(consumer_key=CONSUMER_KEY,
                          consumer_secret=CONSUMER_SECRET,
                          access_token_key=access_token,
                          access_token_secret=access_token_secret)
        profile = api.VerifyCredentials()
        # Create New User with data from twitter profile & random password
        try:
            new_user = User.objects.create_user('%s@twitter' % profile.id, '', access_token_secret)
            if " " in profile.name:
                new_user.first_name = profile.name.split(' ')[0]
                new_user.last_name = profile.name.split(' ')[1]
            else:
                new_user.first_name = profile.name
            new_user.is_active = True
            new_user.save()
            # Save Twitter Data
            twitter_cred = TwitterAuth(user=new_user)
            twitter_cred.access_token = access_token
            twitter_cred.access_token_secret = access_token_secret
            twitter_cred.refresh_profile_data()
            twitter_cred.save()
        except:
            new_user = User.objects.get(username='%s@twitter' % profile.id)
        # Login User
        user = authenticate(username='%s@twitter' % profile.id, password=access_token_secret)
        if user != None:
            login(request, user)
        else:
            raise Exception("Auth Error: %s %s" % ('%s@twitter' % profile.id, access_token_secret))
        # Redirect user
        return HttpResponseRedirect(AUTH_REDIRECT)
    else:
        # Get the temporary credentials for our next few calls
        temp_credentials = twitter_auth.getRequestToken(callback=REGISTER_URL)
        # Save temp_credentials
        request.session['request_token'] = temp_credentials['oauth_token']
        request.session['request_token_secret'] = temp_credentials['oauth_token_secret']
        request.session.modified = True
        # Redirect User to Twitter
        return HttpResponseRedirect(twitter_auth.getAuthorizationURL(temp_credentials, url=AUTHENTICATE_URL))

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
        # Verify User Auth
        api = twitter.Api(consumer_key=CONSUMER_KEY,
                          consumer_secret=CONSUMER_SECRET,
                          access_token_key=access_token,
                          access_token_secret=access_token_secret)
        profile = api.VerifyCredentials()
        # Login User
        user = authenticate(username='%s@twitter' % profile.id, password=access_token_secret)
        if user != None:
            login(request, user)
        else:
            raise Exception("Auth Error: %s %s" % ('%s@twitter' % profile.id, access_token_secret))
        # Redirect user
        return HttpResponseRedirect(AUTH_REDIRECT)
    else:
        # Get the temporary credentials for our next few calls
        temp_credentials = twitter_auth.getRequestToken(callback=LOGIN_URL)
        # Save temp_credentials
        request.session['request_token'] = temp_credentials['oauth_token']
        request.session['request_token_secret'] = temp_credentials['oauth_token_secret']
        request.session.modified = True
        # Redirect User to Twitter
        return HttpResponseRedirect(twitter_auth.getAuthorizationURL(temp_credentials, url=AUTHENTICATE_URL))

def send_tweet(request):
    if request.method == 'POST' and request.POST.has_key('update'):
        if request.user.is_authenticated():
            # Get Access Token
            try:
                access_token = request.user.twitter.access_token
                token_secret = request.user.twitter.access_token_secret
                if access_token == None or token_secret == None:
                    raise Exception('Need to Auth')
            except:
                return HttpResponseRedirect('/%s/auth' % APP_URL_PREFIX)
            # Send Tweet
            api = twitter.Api(consumer_key=CONSUMER_KEY,
                              consumer_secret=CONSUMER_SECRET,
                              access_token_key=access_token,
                              access_token_secret=token_secret)
            status = api.PostUpdate(request.POST['update'])
    if request.META.has_key('HTTP_REFERER'):
        return HttpResponseRedirect(request.META['HTTP_REFERER'])
    else:
        return HttpResponseRedirect("/")


def tweet_form(request):
    # Testing only!!!
    if request.user.is_authenticated():
        # Get Access Token
        try:
            access_token = request.user.twitter.access_token
            token_secret = request.user.twitter.access_token_secret
            if access_token == None or token_secret == None:
                raise Exception('Need to Auth')
        except:
            return HttpResponseRedirect('/%s/auth' % APP_URL_PREFIX)
        # Get user Data
        api = twitter.Api(consumer_key=CONSUMER_KEY,
                          consumer_secret=CONSUMER_SECRET,
                          access_token_key=access_token,
                          access_token_secret=token_secret)
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



    
