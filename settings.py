from django.conf import settings

# Edit these Settings depending on you configuration
AUTH_REDIRECT = '/'           # Location to Redirect to after successful auth
APP_URL_PREFIX = 'twitter'   # URL Prefix set for django_tweet.urls
ALLOW_STAFF = True            # Allow Staff to Auth with Twitter
ALLOW_NON_STAFF = True        # Allow Non-Staff to Auth with Twitter


# You should probably leave these alone
SERVER = 'api.twitter.com'
REQUEST_TOKEN_URL = 'https://api.twitter.com/oauth/request_token'
ACCESS_TOKEN_URL = 'https://api.twitter.com/oauth/access_token'
AUTHORIZATION_URL = 'https://api.twitter.com/oauth/authorize'
CALLBACK_URL = 'http://%s/%s/auth' % (settings.TARGET_HOST, APP_URL_PREFIX)
