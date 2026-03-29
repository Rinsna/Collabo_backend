#!/usr/bin/env python
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'influencer_platform.settings')
django.setup()

from accounts.models import User, InfluencerProfile, CompanyProfile

def create_test_users():
    print("Creating test users with known credentials...")
    
    # Create or update test influencer
    email = 'test@test.com'
    password = 'test123'
    username = 'testuserlogin'
    
    try:
        user = User.objects.get(email=email)
        print(f"User {email} already exists, updating password...")
        user.set_password(password)
        user.save()
    except User.DoesNotExist:
        print(f"Creating new user {email}...")
        user = User.objects.create_user(
            email=email,
            username=username,
            password=password,
            user_type='influencer'
        )
        # Create influencer profile
        InfluencerProfile.objects.get_or_create(user=user)
    
    print(f"✅ Test Influencer created/updated:")
    print(f"   Email: {email}")
    print(f"   Password: {password}")
    print(f"   Type: influencer")
    
    # Create or update test company
    email = 'company@test.com'
    password = 'test123'
    username = 'testcompanylogin'
    
    try:
        user = User.objects.get(email=email)
        print(f"User {email} already exists, updating password...")
        user.set_password(password)
        user.save()
    except User.DoesNotExist:
        print(f"Creating new user {email}...")
        user = User.objects.create_user(
            email=email,
            username=username,
            password=password,
            user_type='company'
        )
        # Create company profile
        CompanyProfile.objects.get_or_create(user=user)
    
    print(f"✅ Test Company created/updated:")
    print(f"   Email: {email}")
    print(f"   Password: {password}")
    print(f"   Type: company")
    
    print("\n🎉 Test users ready! You can now login with:")
    print("   Influencer: test@test.com / test123")
    print("   Company: company@test.com / test123")

if __name__ == "__main__":
    create_test_users()