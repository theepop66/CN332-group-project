import os
import django
from django.test import Client

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'baanhao_project.settings')
django.setup()

from users.models import User

# Grab an existing user if any, or testadmin
user = User.objects.filter(username='testadmin').first()

client = Client()
if user:
    client.force_login(user)

urls_to_test = [
    '/dashboard/',
    '/all_tasks/all_tasks/',
    '/all_tasks/complaint/',
    '/all_tasks/maintenance/',
    '/all_tasks/maintenance/calendar/',
    '/users/staff/',
    '/analytics/',
    '/notifications/',
]

for url in urls_to_test:
    response = client.get(url, HTTP_HOST='127.0.0.1')
    print(f"{url} -> {response.status_code}")

