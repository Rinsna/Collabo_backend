#!/usr/bin/env python
import os
import django
import requests
import json
from datetime import datetime, timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'influencer_platform.settings')
django.setup()

from accounts.models import User
from rest_framework_simplejwt.tokens import RefreshToken

# Get a company user
company_user = User.objects.filter(user_type='company').first()
if not company_user:
    print("No company user found!")
    exit()

print(f"Testing with company user: {company_user.username}")

# Generate JWT token
refresh = RefreshToken.for_user(company_user)
access_token = str(refresh.access_token)

# Test campaign creation
campaign_data = {
    "title": "Test Campaign",
    "description": "This is a test campaign",
    "campaign_type": "sponsored_post",
    "budget": "1000.00",
    "target_audience": "Young adults",
    "requirements": "Must have 10k+ followers",
    "deliverables": "1 Instagram post",
    "deadline": (datetime.now() + timedelta(days=30)).isoformat(),
    "status": "active"
}

headers = {
    'Authorization': f'Bearer {access_token}',
    'Content-Type': 'application/json'
}

try:
    response = requests.post(
        'http://localhost:8000/api/collaborations/campaigns/',
        data=json.dumps(campaign_data),
        headers=headers
    )
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")
    
    if response.status_code == 201:
        print("Campaign created successfully!")
    else:
        print("Campaign creation failed!")
        
except requests.exceptions.RequestException as e:
    print(f"Request failed: {e}")