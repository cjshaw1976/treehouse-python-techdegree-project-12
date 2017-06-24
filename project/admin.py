from django.contrib import admin

from . import models

admin.site.register(models.Project)
admin.site.register(models.ProjectPosition)
admin.site.register(models.ProjectPositionSkill)
admin.site.register(models.ProjectPositionApplication)
