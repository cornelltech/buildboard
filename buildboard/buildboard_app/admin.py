from django.contrib import admin

from .models import Semester, Company, Tag, Project, Student, Membership

# Register your models here.


admin.site.register(Semester)
admin.site.register(Company)
admin.site.register(Tag)
admin.site.register(Project)
admin.site.register(Student)
admin.site.register(Membership)