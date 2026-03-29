#!/usr/bin/env python
import os
import django
import requests
import json

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'influencer_platform.settings')
django.setup()

from accounts.models import User
from collaborations.models import Campaign, CollaborationRequest
from rest_framework_simplejwt.tokens import RefreshToken

# Get an influencer user who hasn't applied to any campaigns yet
influencer_users = User.objects.filter(user_type='influencer')
campaign = Campaign.objects.first()

# Find an influencer who hasn't applied to this campaign
available_influencer = None
for influencer in influencer_users:
    existing_request = CollaborationRequest.objects.filter(
        campaign=campaign,
        influencer=influencer
    ).first()
    if not existing_request:
        available_influencer = influencer
        break

if not available_influencer:
    print("All influencers have already applied to this campaign!")
    # Let's create a new campaign for testing
    from accounts.models import User
    company = User.objects.filter(user_type='company').first()
    new_campaign = Campaign.objects.create(
        company=company,
        title="New Test Campaign",
        description="A new campaign for testing applications",
        campaign_type="sponsored_post",
        budget=1500.00,
        target_audience="Tech enthusiasts",
        requirements="Must have tech background",
        deliverables="1 sponsored post",
        deadline="2026-03-15T12:00:00Z",
        status="active"
    )
    campaign = new_campaign
    available_influencer = influencer_users.first()
    print(f"Created new campaign: {campaign.title} (ID: {campaign.id})")

print(f"Testing with influencer user: {available_influencer.username}")
print(f"Testing with campaign: {campaign.title} (ID: {campaign.id})")

# Generate JWT token
refresh = RefreshToken.for_user(available_influencer)
access_token = str(refresh.access_token)

# Test collaboration request creation
request_data = {
    "campaign": campaign.id,
    "message": "I'm excited to work on this new campaign!",
    "proposed_rate": "900.00"
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
        
except requests.exceptions.RequestException as e:
    print(f"Request failed: {e}")