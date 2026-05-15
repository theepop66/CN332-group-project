from django.db import models
from django.conf import settings

class VisitorPass(models.Model):
    pass_id = models.CharField(max_length=255)
    visitor_name = models.CharField(max_length=255)
    license_plate = models.CharField(max_length=255, null=True, blank=True)
    schedule_date = models.DateTimeField()
    qr_code_string = models.CharField(max_length=255, null=True, blank=True)
    status = models.CharField(max_length=255)
    entry_time = models.DateTimeField(null=True, blank=True)
    exit_time = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    house = models.ForeignKey('properties.House', on_delete=models.CASCADE)

    class Meta:
        db_table = 'visitors_visitorpass'

class VisitLog(models.Model):
    visitor_name = models.CharField(max_length=255)
    license_plate = models.CharField(max_length=255)
    line_user_id = models.CharField(max_length=255, null=True, blank=True)
    house_number = models.CharField(max_length=255, null=True, blank=True)
    status = models.CharField(max_length=255, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    class Meta:
        db_table = 'visit_logs'
