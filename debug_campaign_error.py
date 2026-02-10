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

# Test with the exact same data format that frontend might send
campaign_data = {
    "title": "Test Campaign",
    "description": "This is a test campaign",
    "campaign_type": "sponsored_post",
    "budget": "1000",  # Note: string format like frontend form
    "target_audience": "Young adults",
    "requirements": "Must have 10k+ followers",
    "deliverables": "1 Instagram post",
    "deadline": "2026-03-06T12:00:00",  # datetime-local format
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
    print(f"Response Headers: {dict(response.headers)}")
    print(f"Response Text: {response.text}")
    
    if response.status_code != 201:
        try:
            error_data = response.json()
            print(f"Error Details: {json.dumps(error_data, indent=2)}")
        except:
            print("Could not parse error response as JSON")
        
except requests.exceptions.RequestException as e:
    print(f"Request failed: {e}")