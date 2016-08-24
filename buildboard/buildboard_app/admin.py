from django.contrib import admin
from reversion.admin import VersionAdmin

from buildboard_app.models import Semester, Company, Tag, Project, StudioView


# Register your models here.
@admin.register(Project)
class ProjectAdmin(VersionAdmin):
    pass

admin.site.register(Semester)
admin.site.register(Company)
admin.site.register(Tag)
admin.site.register(StudioView)