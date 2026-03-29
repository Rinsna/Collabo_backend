#!/usr/bin/env python
import os
import django
import requests
import json

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'influencer_platform.settings')
django.setup()

from accounts.models import User
from collaborations.models import Campaign
from rest_framework_simplejwt.tokens import RefreshToken

# Get an influencer user
influencer_user = User.objects.filter(user_type='influencer').first()
if not influencer_user:
    print("No influencer user found!")
    exit()

# Get a campaign
campaign = Campaign.objects.first()
if not campaign:
    print("No campaign found!")
    exit()

print(f"Testing with influencer user: {influencer_user.username}")
print(f"Testing with campaign: {campaign.title} (ID: {campaign.id})")

# Generate JWT token
refresh = RefreshToken.for_user(influencer_user)
access_token = str(refresh.access_token)

# Test collaboration request creation (applying to campaign)
request_data = {
    "campaign": campaign.id,
    "message": "I would love to work on this campaign!",
    "proposed_rate": "800.00"
}

headers = {
    'Authorization': f'Bearer {access_token}',
    'Content-Type': 'application/json'
}

try:
    response = requests.post(
        'http://localhost:8000/api/collaborations/requests/',
        data=json.dumps(request_data),
        headers=headers
    )
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")
    
    if response.status_code == 201:
        print("Application submitted successfully!")
    else:
        print("Application submission failed!")
        try:
            error_data = response.json()
            print(f"Error Details: {json.dumps(error_data, indent=2)}")
        except:
            print("Could not parse error response as JSON")
        
except requests.exceptions.RequestException as e:
    print(f"Request failed: {e}")