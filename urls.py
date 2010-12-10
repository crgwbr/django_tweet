from django.conf import settings
from django.conf.urls.defaults import *

urlpatterns = patterns('',
    url(r'register$', 'django_tweet.views.login_with_twitter'),
    url(r'auth$', 'django_tweet.views.authorize_with_twitter'),
    url(r'post$', 'django_tweet.views.send_tweet'),
    url(r'test$', 'django_tweet.views.tweet_form'),

    url(r'add_facebook$', 'django_tweet.views.authorize_with_facebook'),
    url(r'facebook_login$', 'django_tweet.views.login_with_facebook'),
)
