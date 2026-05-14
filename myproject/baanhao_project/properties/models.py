from django.db import models
from django.utils import timezone


class House(models.Model):
    """properties_house — DDL (no owner FK; owner via Resident.is_owner)."""

    class Meta:
        db_table = 'properties_house'

    house_id = models.CharField(max_length=20, unique=True, help_text='Ex. A-101')
    house_number = models.CharField(max_length=20, help_text='Ex. 99/101')
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f'House {self.house_number} (ID: {self.house_id})'


class Vehicle(models.Model):
    """properties_vehicle — DDL."""

    class Meta:
        db_table = 'properties_vehicle'

    house = models.ForeignKey(House, on_delete=models.CASCADE, related_name='vehicles')
    license_plate = models.CharField(max_length=20)
    brand = models.CharField(max_length=50, blank=True, null=True)
    color = models.CharField(max_length=30, blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f'{self.license_plate} ({self.house.house_number})'
