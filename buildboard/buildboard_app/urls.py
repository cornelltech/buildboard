from django.conf.urls import url, include
from . import views

urlpatterns = [
    url(r'^$', views.index),
    url(r'^(?P<year>(\d{4}))/(?P<semester_type>(fall|spring))$', views.listSemesterProjects, name='list-semester-projects'),
    url(r'^accounts/', include('django.contrib.auth.urls', namespace='accounts')),
]
