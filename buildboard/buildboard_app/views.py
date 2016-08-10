from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required

from .models import Semester

def index(request):
  most_recent_semester = Semester.objects.last()
  if most_recent_semester.is_private:
    return render(request, 'index.html', {
      'semester_studio_title': most_recent_semester.semester_studio_title,
      'semester_studio_description': most_recent_semester.semester_studio_description
    })
  else:
    redirect('listSemesterProjects', 
      year=most_recent_semester.year,
      semester_type=most_recent_semester.semester_type,
    )


def listSemesterProjects(request, year, semester_type):
  return render(request, 'index.html', {})
  

