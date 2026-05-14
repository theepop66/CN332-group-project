import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'baanhao_project.settings')
django.setup()

from users.models import User

user = User.objects.filter(username='testadmin').first()
if user:
    print(f"Yes, testadmin exists. Created at: {user.date_joined}")
else:
    print("testadmin does not exist.")

