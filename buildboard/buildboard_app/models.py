from __future__ import unicode_literals
import reversion
import datetime


from django.db import models
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse

from accounts.models import Account

# Create your models here.
class Semester(models.Model):
    class Meta:
      unique_together = ('semester_type', 'year')
      ordering = ('-year', '-semester_type')

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
    for r in range(1980, (datetime.datetime.now().year+1)):
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
    ordering = ['name']

  def __unicode__(self):
   return self.name

  name = models.CharField(max_length=50, unique=True)
  url = models.URLField()
  description = models.TextField()
  logo = models.ImageField(upload_to='uploads/logo/')

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
    return '%s: %s' % (self.company, self.one_liner)

  one_liner = models.TextField(max_length=250)
  narrative = models.TextField(max_length=500)

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

  @property
  def get_member_emails(self):
    emails = []
    for member in self.members.all():
      emails.append(member.user.email)

    return "mailto: " + ", ".join(emails)

class StudioView(models.Model):
  
  name = models.TextField(max_length=250)
  description = models.TextField(max_length=500)
  url_identifier = models.TextField(max_length=50, unique=True)
  projects = models.ManyToManyField(Project)
