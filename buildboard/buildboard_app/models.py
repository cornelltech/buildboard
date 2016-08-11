from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User
import reversion
import datetime

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
  def __unicode__(self):
    return '%s: %s' % (self.company, self.one_liner)

  one_liner = models.TextField(max_length=250)
  narrative = models.TextField(max_length=500)


  semester = models.ForeignKey(
    Semester,
    on_delete=models.PROTECT
  )

  company = models.ForeignKey(
    Company,
    on_delete=models.PROTECT
  )

  tags = models.ManyToManyField(Tag)


class Student(models.Model):
  def __unicode__(self):
    return self.user.__unicode__()

  user = models.OneToOneField(User, on_delete=models.CASCADE)
  models.ManyToManyField(
          Project,
          through='Membership',
          through_fields=('project', 'student'),
  )



class Membership(models.Model):
  def __unicode__(self):
    return '%s->%s' % (self.student, self.project)
  project = models.ForeignKey(Project, on_delete=models.CASCADE)
  student = models.ForeignKey(Student, on_delete=models.CASCADE)
  inviter = models.ForeignKey(
    Student,
    on_delete=models.CASCADE,
    related_name="membership_invites",
  )
