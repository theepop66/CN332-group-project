import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('issues', '0002_alter_issue_status'),
        ('notifications', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='notification',
            name='user',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name='notifications',
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name='notification',
            name='issue',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='notifications',
                to='issues.issue',
            ),
        ),
        migrations.AddField(
            model_name='notification',
            name='notification_type',
            field=models.CharField(
                choices=[
                    ('issue_update', 'Issue update'),
                    ('announcement', 'Announcement'),
                    ('payment', 'Payment'),
                    ('visitor', 'Visitor'),
                    ('event', 'Event'),
                    ('system', 'System'),
                ],
                default='system',
                max_length=50,
                verbose_name='type',
            ),
        ),
        migrations.AddField(
            model_name='notification',
            name='is_read',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterModelOptions(
            name='notification',
            options={'ordering': ['-created_at']},
        ),
    ]
