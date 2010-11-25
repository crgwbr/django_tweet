#Installation Instructions
1. Copy the django_tweet directory into you Django project
2. Edit `settings.py` to include:
    TARGET_HOST = 'localhost:8000'    # Replace localhost:8000 with your domain
	INSTALLED_APPS = (
	    ...                           # Other Installed Apps before or after
        'devproject.django_tweet',    # Replace devproject with your project name
		...                           
		)
3. Add this to your `urls.py`
    # Django Tweet
    (r'^twitter/', include('django_tweet.urls')),
4. Edit `django_tweet/settings.py` to fit your prefs:
    AUTH_REDIRECT = '/'           # Location to Redirect to after successful auth
    APP_URL_PREFIX = 'twitter'    # URL Prefix set for django_tweet.urls
    ALLOW_STAFF = True            # Allow Staff to Auth with Twitter
    ALLOW_NON_STAFF = True        # Allow Non-Staff to Auth with Twitter
5. Run `./manage.py syncdb` to create django_tweet's tables
	
# Usage
This app is nowhere near complete.  Right now there are only 3 working functions.

*  `/twitter/auth` Send Users here to OAuth with Twitter.  They must be logged in with Django's Auth system
*  `/twitter/post` Direct POST forms here with update="....." to post updates to twitter. If the user hasn't auth'd yet, they get sent to `/twitter/auth`
*  `/twitter/test` A very rough *testing only* update form. Shows some basic user info and enables posting updates