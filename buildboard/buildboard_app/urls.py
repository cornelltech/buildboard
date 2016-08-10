from django.conf.urls import url, include
from . import views

urlpatterns = [
    url(r'^$', views.index),
    url(r'^/(?P<year>(\d{4}))/(?P<semester>(fall|spring))$', views.listSemesterProjects),
    url(r'^accounts/', include('django.contrib.auth.urls', namespace='accounts')),
]
