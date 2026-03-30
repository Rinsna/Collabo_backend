import os
import django
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'influencer_platform.settings')
django.setup()

from accounts.models import User

def seed_superuser():
    email = os.environ.get('DJANGO_SUPERUSER_EMAIL', 'rinsnac44@gmail.com')
    password = os.environ.get('DJANGO_SUPERUSER_PASSWORD', 'admin123')
    username = os.environ.get('DJANGO_SUPERUSER_USERNAME', 'admin')

    print(f">>> Checking for admin user: {email}")

    # First, check if the target email already exists (e.g. was created as company)
    existing_user = User.objects.filter(email=email).first()

    if existing_user:
        print(f">>> Found existing user ({existing_user.user_type}). Upgrading to superuser/admin...")
        existing_user.user_type = 'admin'
        existing_user.is_staff = True
        existing_user.is_superuser = True
        existing_user.is_approved = True
        existing_user.approval_status = 'approved'
        existing_user.username = username
        existing_user.set_password(password)
        existing_user.save()
        print(f">>> Successfully upgraded {email} to superuser/admin!")
    else:
        print(f">>> No existing user found. Creating superuser: {email}")
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

if __name__ == '__main__':
    seed_superuser()
