from django.contrib import admin

from .models import Regulation


@admin.register(Regulation)
class RegulationAdmin(admin.ModelAdmin):
    list_display = ('rule_id', 'topic', 'category', 'last_updated')
    search_fields = ('rule_id', 'topic', 'keywords', 'content')
