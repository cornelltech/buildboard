from django.conf.urls import url, include
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    url(r'^$', views.index),
    url(r'^(?P<year>(\d{4}))/(?P<semester_type>(fall|spring))$', views.listSemesterProjects, name='list-semester-projects'),
    url(r'^project/(?P<pk>[0-9]+)/$', views.ProjectUpdateView.as_view(), name='project-update'),
    url(r'^project$', views.ProjectCreateView.as_view(), name='project-create'),
    url(r'^company/(?P<pk>[0-9]+)/$', views.CompanyUpdateView.as_view(), name='company-update'),
    url(r'^company$', views.CompanyCreateView.as_view(), name='company-create'),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
