from django.contrib import admin

from .models import Complaint, Issue, IssueStatus, Maintenance


@admin.register(Issue)
class IssueAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'reporter', 'assigned_officer', 'status', 'priority', 'created_date')
    list_filter = ('status', 'priority', 'created_date')
    search_fields = ('title', 'description', 'reporter__user__username', 'reporter__user__first_name')
    readonly_fields = ('created_date', 'updated_at')
    ordering = ('-created_date',)


@admin.register(Complaint)
class ComplaintAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'category', 'status', 'reporter')
    list_filter = ('status', 'category')
    search_fields = ('title', 'reporter__user__username')

    fieldsets = (
        ('Info', {'fields': ('reporter', 'assigned_officer', 'title', 'description', 'category', 'priority')}),
        ('Status', {'fields': ('status', 'location')}),
        ('Evidence', {'fields': ('evidence_image', 'analysis_json')}),
    )


@admin.register(Maintenance)
class MaintenanceAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'equipment_type', 'technician', 'status', 'appointment_date')
    list_filter = ('status', 'equipment_type', 'appointment_date')
    search_fields = ('title', 'technician__user__username')
    actions = ['mark_as_completed']

    def mark_as_completed(self, request, queryset):
        queryset.update(status=IssueStatus.RESOLVED)

    mark_as_completed.short_description = 'Mark selected tasks as resolved'
