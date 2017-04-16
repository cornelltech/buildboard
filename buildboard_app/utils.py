from django.core.urlresolvers import reverse

from .models import Semester

def get_semester_nav_links(): 
  semesters = Semester.objects.all()
  semester_nav = {}
  for semester in semesters:
    title = semester.semester_studio_title
    if title not in semester_nav.keys():
      semester_nav[title] = []
    
    semester_nav[title].append({
      'text': '%s %s' % (semester.semester_type, semester.year),
      'url': reverse('buildboard:list-semester-projects',
        kwargs={
          'year': semester.year,
          'semester_type': semester.semester_type.lower()
          }
      ),
    })
  return semester_nav