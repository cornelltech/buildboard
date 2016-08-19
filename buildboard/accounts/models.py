from __future__ import unicode_literals

from django.db import models
from django.db.models.signals import post_save
from django.contrib.auth.models import User

from django.conf import settings
from django.dispatch import receiver

# Create your models here.
class Account(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    slug = models.CharField(max_length=200, blank=True)
    avatar = models.URLField(blank=True)

    def __str__(self):
        return '{user}'.format(user=self.user.username)

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_account(sender, instance=None, created=False, **kwargs):
    if created:
        Account.objects.create(user=instance)
