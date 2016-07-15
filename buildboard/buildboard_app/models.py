from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User

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

    year = models.DateField('semester year')

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
  logo = models.ImageField(upload_to='/uploads/logo/')

class Tags(models.Model):
  name = models.CharField(max_length=50)

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

  tags = models.ManyToManyField(Tags)


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
