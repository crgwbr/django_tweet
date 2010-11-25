from django.db import models
from django.contrib.auth.models import User


class TwitterAuth(models.Model):
    user = models.OneToOneField(User, related_name='twitter')
    request_token = models.TextField(null=True)
    request_token_secret = models.TextField(null=True)

    access_token = models.TextField(null=True)
    access_token_secret = models.TextField(null=True)
    

    def __unicode__(self):
        return "%s | %s" % (self.user.username, self.user.email)
