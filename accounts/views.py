from django.shortcuts import render
from models import Account
from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from buildboard_app.utils import get_semester_nav_links
# Create your views here.
from django.shortcuts import get_object_or_404

@login_required
def profile(request):
  account = Account.objects.get(user__email=request.user.email)
  projects = account.project_set.all()

  return render(request, 'profile.html', {
     'semester_nav_links': get_semester_nav_links(),
     'projects': projects,
  })