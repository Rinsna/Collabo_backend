#!/usr/bin/env python
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'influencer_platform.settings')
django.setup()

from accounts.models import User

print("=== User Debug ===")
users = User.objects.all()

if users.exists():
    print(f"Found {users.count()} users:")
    for user in users:
        print(f"- Email: {user.email}")
        print(f"  Username: {user.username}")
        print(f"  User Type: {user.user_type}")
        print(f"  Is Active: {user.is_active}")
        print(f"  Has Password: {bool(user.password)}")
        print()
else:
    print("No users found in database")
    print("Creating test users...")
    
    # Create test influencer
    influencer = User.objects.create_user(
        email='influencer@test.com',
        username='testinfluencer',
        password='testpass123',
        user_type='influencer'
    )
    print(f"Created influencer: {influencer.email}")
    
    # Create test company
    company = User.objects.create_user(
        email='company@test.com',
        username='testcompany',
        password='testpass123',
        user_type='company'
    )
    print(f"Created company: {company.email}")
    
    print("Test users created successfully!")