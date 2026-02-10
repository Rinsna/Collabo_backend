#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'influencer_platform.settings')
django.setup()

from collaborations.models import CollaborationRequest
from accounts.models import User

print("All collaboration requests:")
requests = CollaborationRequest.objects.all()
for req in requests:
    print(f"ID: {req.id}, Campaign: {req.campaign.title}, Influencer: {req.influencer.username}, Company: {req.company.username}, Status: {req.status}")

print("\nAll users:")
users = User.objects.all()
for user in users:
    print(f"ID: {user.id}, Username: {user.username}, Type: {user.user_type}")

# Check if request ID 2 exists
try:
    req = CollaborationRequest.objects.get(id=2)
    print(f"\nRequest ID 2 exists:")
    print(f"Campaign: {req.campaign.title}")
    print(f"Influencer: {req.influencer.username}")
    print(f"Company: {req.company.username}")
    print(f"Status: {req.status}")
except CollaborationRequest.DoesNotExist:
    print("\nRequest ID 2 does not exist!")