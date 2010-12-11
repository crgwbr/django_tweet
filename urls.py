from django.conf import settings
from django.conf.urls.defaults import *

urlpatterns = patterns('',
    url(r'add_twitter$', 'django_tweet.views.authorize_with_twitter'),
    url(r'twitter_login$', 'django_tweet.views.login_with_twitter'),

    url(r'twitter_post$', 'django_tweet.views.send_tweet'),
    url(r'twitter_form$', 'django_tweet.views.tweet_form'),

    url(r'add_facebook$', 'django_tweet.views.authorize_with_facebook'),
    url(r'facebook_login$', 'django_tweet.views.login_with_facebook'),
)
