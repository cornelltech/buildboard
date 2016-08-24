from django.shortcuts import render, redirect
from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.views.generic.edit import UpdateView

from buildboard_app.models import Semester, Project
from .utils import get_semester_nav_links

def index(request):
  most_recent_semester = Semester.objects.last()
  if most_recent_semester.is_private:
    return render(request, 'index.html', {
      'semester_nav_links': get_semester_nav_links(),
      'semester_studio_title': most_recent_semester.semester_studio_title,
      'semester_studio_description': most_recent_semester.semester_studio_description
    })
  else:
    return redirect('buildboard:list-semester-projects',
      year='2016',
      semester_type='fall',
    )


def listSemesterProjects(request, year, semester_type):
  semester_type = semester_type.upper()
  semester = Semester.objects.get(year=year,semester_type=semester_type)

  if semester.is_private:
     return render(request, 'index.html', {
      'semester_nav_links': get_semester_nav_links(),
      'semester_studio_title': semester.semester_studio_title,
      'semester_studio_description': semester.semester_studio_description
    })
   
  projects = semester.project_set.all()

  project_list = []

  for project in projects:
    project_info = {}

    project_info["one_liner"] = project.one_liner
    project_info["narrative"] = project.narrative
    project_info["company"] = {
      'logo': project.company.logo.url,
      'name': project.company.name,
      'url': project.company.url,
      'description': project.company.description
    }

    project_info["students"] = []

    for member in project.members.all():
       project_info["students"].append(member.user.first_name)

    project_list.append(project_info)

  return render(request, 'list.html', {
    'semester_nav_links': get_semester_nav_links(),
    'semester_studio_title': semester.semester_studio_title,
    'semester_studio_description': semester.semester_studio_description,
    'project_list': project_list,
  })

class ProjectUpdateView(UpdateView):
  model = Project
  fields=["one_liner", "narrative", "company", "tags"]
  template_name_suffix = '_update_form'
