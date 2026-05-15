from django.db import models

class Regulation(models.Model):
    rule_id = models.CharField(max_length=255)
    category = models.CharField(max_length=255)
    topic = models.CharField(max_length=255)
    content = models.TextField()
    keywords = models.CharField(max_length=255, null=True, blank=True)
    last_updated = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'regulations_regulation'
