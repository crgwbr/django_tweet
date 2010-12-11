from django.conf import settings

# Edit these Settings depending on you configuration
AUTH_REDIRECT = '/'           # Location to Redirect to after successful auth
AUTH_DENIED = '/'             # Where to send a user if auth fails  "/?message=Not%20Allowed"
APP_URL_PREFIX = 'twitter'    # URL Prefix set for django_tweet.urls
ALLOW_STAFF = True            # Allow Staff to Auth with Twitter
ALLOW_NON_STAFF = True        # Allow Non-Staff to Auth with Twitter


# You should probably leave these alone
TWITTER_USERNAME_FORMAT = "%s@twitter"
FACEBOOK_USERNAME_FORMAT = "%s@facebook"

TWITTER_AUTHENTICATE_URL = 'https://api.twitter.com/oauth/authenticate'

ADD_TWITTER_URL = 'http://%s/%s/add_twitter' % (settings.TARGET_HOST, APP_URL_PREFIX)
TWITTER_LOGIN_URL = 'http://%s/%s/twitter_login' % (settings.TARGET_HOST, APP_URL_PREFIX)
POST_TO_TWITTER = 'http://%s/%s/twitter_post' % (settings.TARGET_HOST, APP_URL_PREFIX)

ADD_FACEBOOK_URL = 'http://%s/%s/add_facebook' % (settings.TARGET_HOST, APP_URL_PREFIX)
FACEBOOK_LOGIN_URL = 'http://%s/%s/facebook_login' % (settings.TARGET_HOST, APP_URL_PREFIX)
POST_TO_FACEBOOK = 'http://%s/%s/facebook_post' % (settings.TARGET_HOST, APP_URL_PREFIX)
