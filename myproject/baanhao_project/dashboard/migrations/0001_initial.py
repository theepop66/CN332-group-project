import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('users', '0004_registrationrequest'),
    ]

    operations = [
        migrations.CreateModel(
            name='Event',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200)),
                ('description', models.TextField()),
                ('event_date', models.DateTimeField()),
                ('location', models.CharField(max_length=100)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                (
                    'created_by',
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.RESTRICT,
                        related_name='events',
                        to='users.admin',
                    ),
                ),
            ],
            options={
                'ordering': ['event_date'],
            },
        ),
    ]
