from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _


class NotificationType(models.TextChoices):
    ISSUE_UPDATE = 'issue_update', _('Issue update')
    ANNOUNCEMENT = 'announcement', _('Announcement')
    PAYMENT = 'payment', _('Payment')
    VISITOR = 'visitor', _('Visitor')
    EVENT = 'event', _('Event')
    SYSTEM = 'system', _('System')


class Notification(models.Model):
    """Maps to notifications_notification (DDL): user, issue, type, title, message, is_read, created_at."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notifications',
        null=True,
        blank=True,
    )
    issue = models.ForeignKey(
        'issues.Issue',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='notifications',
    )
    notification_type = models.CharField(
        _('type'),
        max_length=50,
        choices=NotificationType.choices,
        default=NotificationType.SYSTEM,
    )
    title = models.CharField(max_length=255)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title