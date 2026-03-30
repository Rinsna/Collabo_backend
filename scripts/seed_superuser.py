import os
import django

import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'influencer_platform.settings')
django.setup()

from accounts.models import User

def seed_superuser():
    email = os.environ.get('DJANGO_SUPERUSER_EMAIL', 'admin@collabo.com')
    password = os.environ.get('DJANGO_SUPERUSER_PASSWORD', 'Admin123!')
    username = os.environ.get('DJANGO_SUPERUSER_USERNAME', 'admin')
    
    if not User.objects.filter(is_superuser=True).exists():
        print(f">>> Creating default superuser: {email}")
        try:
            user = User.objects.create_superuser(
                username=username,
                email=email,
                password=password,
                user_type='admin'
            )
            user.is_approved = True
            user.approval_status = 'approved'
            user.save()
            print(">>> Superuser created successfully!")
        except Exception as e:
            print(f">>> Error creating superuser: {e}")
    else:
        print(">>> Superuser already exists. Skipping creation.")

if __name__ == '__main__':
    seed_superuser()
