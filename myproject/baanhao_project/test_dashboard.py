import os
import django
from django.test import Client

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'baanhao_project.settings')
django.setup()

from users.models import User

user, created = User.objects.get_or_create(username='testadmin')
if created:
    user.set_password('testpass123')
    user.save()

client = Client()
client.force_login(user)

response = client.get('/dashboard/', HTTP_HOST='127.0.0.1')
print(f"/dashboard/ -> {response.status_code}")

