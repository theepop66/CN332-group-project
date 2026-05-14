from django.db import models


class Regulation(models.Model):
    """regulations_regulation — DDL."""

    class Meta:
        db_table = 'regulations_regulation'

    rule_id = models.CharField(max_length=50, unique=True)
    category = models.CharField(max_length=50)
    topic = models.CharField(max_length=200)
    content = models.TextField()
    keywords = models.CharField(max_length=500, blank=True, null=True)
    last_updated = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.topic
