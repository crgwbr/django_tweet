from django.conf import settings
from django.conf.urls.defaults import *

urlpatterns = patterns('',
    url(r'register$', 'django_tweet.views.new_user'),
    url(r'auth$', 'django_tweet.views.authorize'),
    url(r'post$', 'django_tweet.views.send_tweet'),
    url(r'test$', 'django_tweet.views.tweet_form'),
)
