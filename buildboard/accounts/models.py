from __future__ import unicode_literals

from django.db import models
from django.db.models.signals import post_save
from django.contrib.auth.models import User

from django.conf import settings
from django.dispatch import receiver


class OrderedUser(User):
    class Meta:
        ordering = ["first_name", "last_name"]
        proxy = True

# Create your models here.
class Account(models.Model):
    class Meta:
        ordering = ['user']
    user = models.OneToOneField(OrderedUser, on_delete=models.CASCADE)
    slug = models.CharField(max_length=200, blank=True)
    avatar = models.URLField(blank=True)

    def __str__(self):
        return '{first_name} {last_name} ({email})'.format(
            first_name=self.user.first_name,
            last_name=self.user.last_name,
            email=self.user.email)


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_account(sender, instance=None, created=False, **kwargs):
    if created:
        Account.objects.create(user=instance)
