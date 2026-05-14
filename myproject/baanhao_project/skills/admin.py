from django.contrib import admin

from .models import Skill, TechnicianSkill


@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at')
    search_fields = ('name',)


@admin.register(TechnicianSkill)
class TechnicianSkillAdmin(admin.ModelAdmin):
    list_display = ('technician', 'skill')
    list_filter = ('skill',)
