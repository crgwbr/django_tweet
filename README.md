#Installation Instructions
1. Copy the django_tweet directory into you Django project
2. Edit `settings.py` to include:
	    TARGET_HOST = 'localhost:8000'    # Replace localhost:8000 with your domain
        INSTALLED_APPS = (
	        ...                           # Other Installed Apps before or after
            'devproject.django_tweet',    # Replace devproject with your project name
            ...                           
	    )
        AUTHENTICATION_BACKENDS = (
			'devproject.django_tweet.auth.TwitterBackend',
			'devproject.django_tweet.auth.FacebookBackend',
		)		
3. Add this to your `urls.py`
        # Django Tweet
        (r'^twitter/', include('django_tweet.urls')),
4. Edit `django_tweet/settings.py` to fit your prefs:
        AUTH_REDIRECT = '/'           # Location to Redirect to after successful auth
        APP_URL_PREFIX = 'twitter'    # URL Prefix set for django_tweet.urls
        ALLOW_STAFF = True            # Allow Staff to Auth with Twitter
        ALLOW_NON_STAFF = True        # Allow Non-Staff to Auth with Twitter
5. Create `django_tweet/keys.py` and fill in your API keys like this:
        TWITTER_CONSUMER_KEY = 'foo'
        TWITTER_CONSUMER_SECRET = 'bar'
        FACEBOOK_APP_ID = 'FOO'
        FACEBOOK_APP_SECRET = 'BAR'
6. Run `./manage.py syncdb` to create django_tweet's tables
	
# Usage
Right now these are the working functions.

*  `/twitter/add_twitter` Send Users here to OAuth with Twitter.  They must be logged in with Django's Auth system
*  `/twitter/twitter_login` Send anonymous users to create a new account / login via their Twitter account.
*  `/twitter/twitter_post` Direct POST forms here with update="....." to post updates to twitter. If the user hasn't auth'd yet, they get sent to `/twitter/twitter_login`
*  `/twitter/twitter_form` A very rough *testing only* update form. Shows some basic user info and enables posting updates
*  `/twitter/add_facebook` Send Users here to OAuth with Facebook.  They must be logged in with Django's Auth system
*  `/twitter/facebook_login` Send anonymous users to create a new account / login via their Facebook account.

To gain access to the Twitter/Facebook API for a user after they have auth'd do something like this:
        def view_foo(request):
		    # The model pickles & caches profile data, so you don't have to worry about overloading the api
		    twitter_profile = request.user.twitter.get_profile_data()
			facebook_profile = request.user.facebook.get_profile_data()
			
			# You can manually refresh profile data.  Otherwise, get_profile_data() does it every 7 days
			request.user.twitter.refresh_profile_data()
			request.user.facebook.refresh_profile_data()
			
			# Get the Raw API
            twitter_api = request.user.twitter.api()
			facebook_api = request.user.facebook.api()
            
            # Post Something
			twitter_api.PostUpdates("Isn\'t Django Tweet Awesome?!")
			facebook_api.put_wall_post("Isn\'t Django Tweet Awesome?!")
			
For Usage on the actualy API's, please visit:

*  https://github.com/facebook/python-sdk/blob/master/src/facebook.py
*  http://code.google.com/p/python-twitter/