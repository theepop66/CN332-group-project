from django.db import models
from django.conf import settings

class Notification(models.Model):
    title = models.CharField(max_length=255)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.CASCADE)
    issue = models.ForeignKey('issues.Issue', null=True, blank=True, on_delete=models.CASCADE)
    notification_type = models.CharField(max_length=255)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return self.title

    class Meta:
        db_table = 'notifications_notification'