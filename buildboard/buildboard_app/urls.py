from django.conf.urls import url, include
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    url(r'^$', views.index),
    url(r'^(?P<year>(\d{4}))/(?P<semester_type>(fall|spring))$', views.listSemesterProjects, name='list-semester-projects'),
    url(r'^accounts/', include('django.contrib.auth.urls', namespace='accounts')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
