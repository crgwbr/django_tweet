from django.conf import settings
from django.conf.urls.defaults import *

urlpatterns = patterns('',
    url(r'auth$', 'django_tweet.views.authorize'),
)
