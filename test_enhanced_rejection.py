#!/usr/bin/env python
import os
import django
import requests
import json

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'influencer_platform.settings')
django.setup()

from accounts.models import User
from collaborations.models import CollaborationRequest
from rest_framework_simplejwt.tokens import RefreshToken

print("=== Testing Enhanced Rejection with Reason ===\n")

# Find a pending request to test
pending_request = CollaborationRequest.objects.filter(status='pending').first()

if not pending_request:
    print("No pending requests found for testing.")
    exit()

print(f"Testing rejection of request ID: {pending_request.id}")
print(f"Campaign: {pending_request.campaign.title}")
print(f"Influencer: {pending_request.influencer.username}")
print(f"Original message: {pending_request.message}")

# Get the company user
company_user = pending_request.company
refresh = RefreshToken.for_user(company_user)
access_token = str(refresh.access_token)

# Test rejection with reason
rejection_reason = "We decided to go with an influencer who has more experience in the tech industry."
updated_message = f"{pending_request.message}\n\n[REJECTION REASON]: {rejection_reason}"

rejection_data = {
    "status": "rejected",
    "message": updated_message
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
    
    if response.status_code == 200:
        response_data = response.json()
        print("✅ Request rejected successfully with reason!")
        print(f"Updated Status: {response_data['status']}")
        print(f"Updated Message: {response_data['message']}")
        
        # Verify in database
        pending_request.refresh_from_db()
        print(f"\nDatabase verification:")
        print(f"Status: {pending_request.status}")
        print(f"Message contains rejection reason: {'[REJECTION REASON]' in pending_request.message}")
        
    else:
        print(f"❌ Request rejection failed: {response.text}")
        
except requests.exceptions.RequestException as e:
    print(f"❌ Request failed: {e}")

print("\n=== Testing Complete ===")