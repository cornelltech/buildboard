from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User
import reversion
import datetime
YEAR_CHOICES = []
for r in range(1980, (datetime.datetime.now().year+1)):
    YEAR_CHOICES.append((r,r))

# Create your models here.
class Semester(models.Model):
    FALL = 'FALL'
    SPRING = 'SPRING'
    SUMMER = 'SUMMER'

    SEMESTER_TYPE_CHOICES = (
        (FALL, 'Fall'),
        (SPRING, 'Spring'),
        (SUMMER, 'Summer'),
    )

    year = models.IntegerField(max_length=4, choices=YEAR_CHOICES, default=datetime.datetime.now().year)

    semester_type = models.CharField(
      max_length=20,
      choices=SEMESTER_TYPE_CHOICES,
      default=FALL,
      unique_for_year=year
    )

class Company(models.Model):
  name = models.CharField(max_length=50)
  url = models.URLField()
  description = models.TextField()
  logo = models.ImageField(upload_to='uploads/logo/')

class Tag(models.Model):
  name = models.CharField(max_length=50)

@reversion.register()
class Project(models.Model):
  one_liner = models.CharField(max_length=250)
  narrative = models.CharField(max_length=500)


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
  user = models.OneToOneField(User, on_delete=models.CASCADE)
  models.ManyToManyField(
          Project,
          through='Membership',
          through_fields=('project', 'student'),
  )



class Membership(models.Model):
  project = models.ForeignKey(Project, on_delete=models.CASCADE)
  student = models.ForeignKey(Student, on_delete=models.CASCADE)
  inviter = models.ForeignKey(
    Student,
    on_delete=models.CASCADE,
    related_name="membership_invites",
  )
