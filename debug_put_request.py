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

# Check what collaboration requests exist
print("All collaboration requests:")
requests_list = CollaborationRequest.objects.all()
for req in requests_list:
    print(f"ID: {req.id}, Campaign: {req.campaign.title}, Influencer: {req.influencer.username}, Company: {req.company.username}, Status: {req.status}")

# Get a company user
company_user = User.objects.filter(user_type='company').first()
print(f"\nTesting with company user: {company_user.username}")

# Generate JWT token
refresh = RefreshToken.for_user(company_user)
access_token = str(refresh.access_token)

# Test updating collaboration request (rejecting it)
request_data = {
    "status": "rejected"
}

headers = {
    'Authorization': f'Bearer {access_token}',
    'Content-Type': 'application/json'
}

# Test with request ID 3 (if it exists)
request_id = 3
if CollaborationRequest.objects.filter(id=request_id).exists():
    try:
        response = requests.put(
            f'http://localhost:8000/api/collaborations/requests/{request_id}/',
            data=json.dumps(request_data),
            headers=headers
        )
        
        print(f"\nPUT Status Code: {response.status_code}")
        print(f"PUT Response: {response.text}")
        
        if response.status_code != 200:
            try:
                error_data = response.json()
                print(f"Error Details: {json.dumps(error_data, indent=2)}")
            except:
                print("Could not parse error response as JSON")
            
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
else:
    print(f"\nRequest ID {request_id} does not exist")

# Also test with minimal data to see what's required
print("\n--- Testing with minimal data ---")
minimal_data = {}
try:
    response = requests.put(
        f'http://localhost:8000/api/collaborations/requests/1/',
        data=json.dumps(minimal_data),
        headers=headers
    )
    
    print(f"Minimal PUT Status Code: {response.status_code}")
    print(f"Minimal PUT Response: {response.text}")
    
except requests.exceptions.RequestException as e:
    print(f"Minimal request failed: {e}")