from django.contrib import admin
from reversion.admin import VersionAdmin

from .models import Semester, Company, Tag, Project, Student, Membership


# Register your models here.
@admin.register(Project)
class ProjectAdmin(VersionAdmin):
    pass

admin.site.register(Semester)
admin.site.register(Company)
admin.site.register(Tag)
admin.site.register(Student)
admin.site.register(Membership)