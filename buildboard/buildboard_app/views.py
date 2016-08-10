from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required

# Create your views here.


def index(request):
  return render(request, 'index.html', {})


def listSemesterProjects(request):
  return render(request, 'index.html', {})
  

