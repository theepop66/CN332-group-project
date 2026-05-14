from django.contrib import admin

from .models import VisitorPass


@admin.register(VisitorPass)
class VisitorPassAdmin(admin.ModelAdmin):
    list_display = ('pass_id', 'visitor_name', 'house', 'schedule_date', 'status')
    list_filter = ('status',)
