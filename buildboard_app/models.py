from __future__ import unicode_literals

import os
import uuid
import reversion
import datetime


from django.db import models
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse

from accounts.models import Account
from django.conf import settings


def get_team_photo_path(instance, filename):
  ext = filename.split('.')[-1]
  filename = "%s-%s-%s-%s.%s" % (
    instance.company,
    instance.semester.semester_type,
    instance.semester.year,
    uuid.uuid4(),
    ext)
  return os.path.join('uploads/team-photos', filename)

def get_logo_path(instance, filename):
  ext = filename.split('.')[-1]
  filename = "%s-%s.%s" % (instance.name, uuid.uuid4(), ext)
  return os.path.join('uploads/logos', filename)


# Create your models here.
class Semester(models.Model):
    class Meta:
      unique_together = ('semester_type', 'year')
      ordering = ('-year', 'semester_type')

    def __unicode__(self):
      return '%s Semester %d' % (self.semester_type, self.year)

    FALL = 'FALL'
    SPRING = 'SPRING'
    SUMMER = 'SUMMER'

    SEMESTER_TYPE_CHOICES = (
        (FALL, 'Fall'),
        (SPRING, 'Spring'),
        (SUMMER, 'Summer'),
    )

    YEAR_CHOICES = []
    for r in range(1980, (datetime.datetime.now().year + 10)):
        YEAR_CHOICES.append((r,r))

    year = models.IntegerField(choices=YEAR_CHOICES, default=datetime.datetime.now().year)

    semester_type = models.CharField(
      max_length=20,
      choices=SEMESTER_TYPE_CHOICES,
      default=FALL,
    )

    semester_studio_title = models.CharField(max_length=50)

    semester_studio_description = models.TextField(max_length=250)

    url_key = models.CharField(max_length=50)

    is_private = models.BooleanField(
      default=True,
    )

@reversion.register()
class Company(models.Model):
  class Meta:
    unique_together = ('name', 'division')
    ordering = ['name', 'division']

  def __unicode__(self):
   return self.name

  name = models.CharField(max_length=50)
  url = models.URLField(blank=True)
  description = models.TextField(blank=True)

  division = models.CharField(max_length=50, blank=True)

  logo = models.ImageField(upload_to=get_logo_path)

  def get_absolute_url(self):
    return reverse('buildboard:company-update', kwargs={'pk': self.pk})

class Tag(models.Model):
  class Meta:
    ordering = ['name']
  
  def __unicode__(self):
    return self.name

  name = models.CharField(max_length=50)

@reversion.register()
class Project(models.Model):
  class Meta:
    ordering = ['-last_modified']

  def __unicode__(self):
    return '%s-%s: %s' % (self.semester, self.company, self.one_liner)

  one_liner = models.TextField(max_length=250, unique=True)
  product_narrative = models.TextField(max_length=500)

  last_modified = models.DateTimeField(auto_now=True)

  semester = models.ForeignKey(
    Semester,
    on_delete=models.PROTECT
  )

  company = models.ForeignKey(
    Company,
    on_delete=models.PROTECT
  )

  tags = models.ManyToManyField(Tag)

  members = models.ManyToManyField(Account)

  team_photo = models.ImageField(upload_to=get_team_photo_path)

  def get_absolute_url(self):
    return reverse('buildboard:project-update', kwargs={'pk': self.pk})


  @property
  def get_member_emails(self):
    emails = []
    for member in self.members.all():
      emails.append(member.user.email)

    return "mailto:" + ";".join(emails) + "?cc=" + settings.ADMINS[0][1]

class StudioView(models.Model):
  def __unicode__(self):
    return self.url_identifier
  
  name = models.TextField(max_length=250)
  description = models.TextField(max_length=500)
  url_identifier = models.TextField(max_length=50, unique=True)
  projects = models.ManyToManyField(Project)
