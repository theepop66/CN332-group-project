from django.contrib import admin

from .models import Event


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('title', 'event_date', 'location', 'created_by')
    list_filter = ('event_date',)
    search_fields = ('title', 'location', 'description')
