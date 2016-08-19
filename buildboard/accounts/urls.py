from django.conf.urls import url, include
from django.conf import settings
from . import views

urlpatterns = [
    url(r'^accounts/', include('django.contrib.auth.urls')),
    url(r'^accounts/profile', views.profile, name='user-profile'),
]
