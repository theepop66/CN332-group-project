import uuid

from django.db import models


class VisitorPass(models.Model):
    """visitors_visitorpass — DDL."""

    class Meta:
        db_table = 'visitors_visitorpass'

    class PassStatus(models.TextChoices):
        PENDING = 'pending', 'Pending'
        ACTIVE = 'active', 'Active'
        EXPIRED = 'expired', 'Expired'
        CANCELLED = 'cancelled', 'Cancelled'

    pass_id = models.CharField(max_length=50, unique=True, editable=False)
    house = models.ForeignKey(
        'properties.House',
        on_delete=models.CASCADE,
        related_name='visitor_passes',
    )
    created_by = models.ForeignKey(
        'users.Resident',
        on_delete=models.RESTRICT,
        related_name='created_visitor_passes',
    )
    visitor_name = models.CharField(max_length=100)
    license_plate = models.CharField(max_length=20, blank=True, null=True)
    schedule_date = models.DateTimeField()
    qr_code_string = models.CharField(max_length=500, blank=True, null=True)
    status = models.CharField(
        max_length=20,
        choices=PassStatus.choices,
        default=PassStatus.PENDING,
    )
    entry_time = models.DateTimeField(blank=True, null=True)
    exit_time = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.pass_id:
            self.pass_id = f'VP-{uuid.uuid4().hex[:12].upper()}'
        super().save(*args, **kwargs)

    def __str__(self):
        return self.pass_id
