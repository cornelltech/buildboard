from __future__ import unicode_literals
import reversion
import datetime


from django.db import models
from django.contrib.auth.models import User
from accounts.models import Account

# Create your models here.
class Semester(models.Model):
    class Meta:
      unique_together = ('semester_type', 'year')
      ordering = ('year', '-semester_type')

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

    year = models.IntegerField(max_length=4, choices=YEAR_CHOICES, default=datetime.datetime.now().year)

    semester_type = models.CharField(
      max_length=20,
      choices=SEMESTER_TYPE_CHOICES,
      default=FALL,
    )

    semester_studio_title = models.CharField(max_length=50)

    semester_studio_description = models.TextField(max_length=250)

    is_private = models.BooleanField(
      default=True,
    )

class Company(models.Model):
  def __unicode__(self):
   return self.name

  name = models.CharField(max_length=50)
  url = models.URLField()
  description = models.TextField()
  logo = models.ImageField(upload_to='media/uploads/logo/')

class Tag(models.Model):
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

class StudioView(models.Model):
  
  name = models.TextField(max_length=250)
  description = models.TextField(max_length=500)
  url_identifier = models.TextField(max_length=50, unique=True)
  projects = models.ManyToManyField(Project)