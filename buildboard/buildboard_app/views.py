from django.shortcuts import render, redirect
from django.core.urlresolvers import reverse, reverse_lazy
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.views.generic.edit import CreateView, UpdateView

from buildboard_app.models import Semester, Project, Company, StudioView
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


def listSemesterProjects(request, year, semester_type, url_key=None):
  semester_type = semester_type.upper()
  semester = Semester.objects.get(year=year,semester_type=semester_type)

  is_url_key_valid = url_key != None and url_key == semester.url_key

  if (not semester.is_private) or is_url_key_valid:
    projects = semester.project_set.all()

    return render(request, 'list.html', {
      'semester_nav_links': get_semester_nav_links(),
      'semester_studio_title': semester.semester_studio_title,
      'semester_studio_description': semester.semester_studio_description,
      'projects': projects,
      'is_url_key_valid': is_url_key_valid
    })

  return render(request, 'index.html', {
    'semester_nav_links': get_semester_nav_links(),
    'semester_studio_title': semester.semester_studio_title,
    'semester_studio_description': semester.semester_studio_description
  })

def studioView(request, slug):
  studio_details = StudioView.objects.get(url_identifier=slug)


  return render(request, 'buildboard_app/studio_list.html', {
    'name': studio_details.name,
    'description': studio_details.description,
    'projects': studio_details.projects.all()
  })


class ProjectCreateView(CreateView):
  model = Project
  success_url = reverse_lazy('accounts:user-profile')
  fields=["one_liner", "narrative", "company", "tags", "members"]
  template_name_suffix = '_create_form'


class ProjectUpdateView(UpdateView):
  model = Project
  success_url = reverse_lazy('accounts:user-profile')
  fields = ["one_liner", "narrative", "company", "tags", "members"]
  template_name_suffix = '_update_form'

class CompanyCreateView(CreateView):
  model = Company
  success_url = reverse_lazy('accounts:user-profile')
  fields=["name", "url", "description", "logo"]
  template_name_suffix = '_create_form'


class CompanyUpdateView(UpdateView):
  model = Company
  success_url = reverse_lazy('accounts:user-profile')
  fields=["name", "url", "description", "logo"]
  template_name_suffix = '_update_form'
