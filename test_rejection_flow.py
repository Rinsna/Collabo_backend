#!/usr/bin/env python
import os
import django
import requests
import json

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'influencer_platform.settings')
django.setup()

from accounts.models import User
from collaborations.models import CollaborationRequest, Campaign
from rest_framework_simplejwt.tokens import RefreshToken

print("=== Testing Collaboration Request Rejection Flow ===\n")

# First, let's see all current collaboration requests
print("Current collaboration requests:")
requests_list = CollaborationRequest.objects.all()
for req in requests_list:
    print(f"ID: {req.id}, Campaign: {req.campaign.title}, Influencer: {req.influencer.username}, Company: {req.company.username}, Status: {req.status}")

# Find a pending request to test rejection
pending_request = CollaborationRequest.objects.filter(status='pending').first()

if not pending_request:
    print("\nNo pending requests found. Creating a test request...")
    
    # Create a test request
    influencer = User.objects.filter(user_type='influencer').first()
    campaign = Campaign.objects.first()
    
    if influencer and campaign:
        pending_request = CollaborationRequest.objects.create(
            campaign=campaign,
            influencer=influencer,
            company=campaign.company,
            message="Test request for rejection",
            proposed_rate=600.00,
            status='pending'
        )
        print(f"Created test request ID: {pending_request.id}")
    else:
        print("Could not create test request - missing influencer or campaign")
        exit()

print(f"\nTesting rejection of request ID: {pending_request.id}")
print(f"Campaign: {pending_request.campaign.title}")
print(f"Influencer: {pending_request.influencer.username}")
print(f"Company: {pending_request.company.username}")
print(f"Current Status: {pending_request.status}")

# Get the company user who owns this request
company_user = pending_request.company
print(f"\nTesting with company user: {company_user.username}")

# Generate JWT token for the company
refresh = RefreshToken.for_user(company_user)
access_token = str(refresh.access_token)

# Test rejecting the collaboration request
rejection_data = {
    "status": "rejected"
}

headers = {
    'Authorization': f'Bearer {access_token}',
    'Content-Type': 'application/json'
}

try:
    response = requests.put(
        f'http://localhost:8000/api/collaborations/requests/{pending_request.id}/',
        data=json.dumps(rejection_data),
        headers=headers
    )
    
    print(f"\nRejection API Response:")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")
    
    if response.status_code == 200:
        print("\n✅ Request rejected successfully!")
        
        # Verify the status was updated in the database
        pending_request.refresh_from_db()
        print(f"Updated Status in DB: {pending_request.status}")
        
        if pending_request.status == 'rejected':
            print("✅ Database status correctly updated to 'rejected'")
        else:
            print(f"❌ Database status is '{pending_request.status}', expected 'rejected'")
    else:
        print("❌ Request rejection failed!")
        
except requests.exceptions.RequestException as e:
    print(f"❌ Request failed: {e}")

print("\n=== Testing Complete ===")