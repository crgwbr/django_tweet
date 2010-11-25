# Twitter OAuth Client

#from django.conf import settings
import oauth2 as oauth
import oauthtwitter
import pprint

SERVER = 'api.twitter.com'
REQUEST_TOKEN_URL = 'https://api.twitter.com/oauth/request_token'
ACCESS_TOKEN_URL = 'https://api.twitter.com/oauth/access_token'
AUTHORIZATION_URL = 'https://api.twitter.com/oauth/authorize'

CALLBACK_URL = 'http://%s/admin' % "localhost:8000"

CONSUMER_KEY = 'Uu4u7E8a8OrCB9Hijrj4g'
CONSUMER_SECRET = 'rOlgsksdt8RXvJSU4jFno1aealePVYd7kn744rgH8'



twitter = oauthtwitter.OAuthApi(CONSUMER_KEY, CONSUMER_SECRET)

# Get the temporary credentials for our next few calls
temp_credentials = twitter.getRequestToken()

# User pastes this into their browser to bring back a pin number
print(twitter.getAuthorizationURL(temp_credentials))

















