from django.db import models


class Event(models.Model):
    """Maps to events_event in DDL: created_by → Admin, title, description, event_date, location, timestamps."""

    created_by = models.ForeignKey(
        'users.Admin',
        on_delete=models.RESTRICT,
        related_name='events',
    )
    title = models.CharField(max_length=200)
    description = models.TextField()
    event_date = models.DateTimeField()
    location = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'events_event'
        ordering = ['event_date']

    def __str__(self):
        return self.title
