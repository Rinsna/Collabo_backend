#!/usr/bin/env python
import os
import django
import requests
import json

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'influencer_platform.settings')
django.setup()

from accounts.models import User
from rest_framework_simplejwt.tokens import RefreshToken

# Get a company user
company_user = User.objects.filter(user_type='company').first()
if not company_user:
    print("No company user found!")
    exit()

print(f"Testing with company user: {company_user.username} (type: {company_user.user_type})")

# Generate JWT token
refresh = RefreshToken.for_user(company_user)
access_token = str(refresh.access_token)

# Test with problematic data that might come from frontend
test_cases = [
    {
        "name": "Empty strings",
        "data": {
            "title": "",
            "description": "",
            "campaign_type": "",
            "budget": "",
            "deadline": "",
        }
    },
    {
        "name": "Missing required fields",
        "data": {
            "title": "Test Campaign"
        }
    },
    {
        "name": "Invalid datetime format",
        "data": {
            "title": "Test Campaign",
            "description": "Test description",
            "campaign_type": "sponsored_post",
            "budget": "1000",
            "deadline": "2026-03-06T12:00",  # No timezone
            "target_audience": "Test audience",
            "requirements": "Test requirements",
            "deliverables": "Test deliverables",
            "status": "active"
        }
    },
    {
        "name": "Invalid campaign type",
        "data": {
            "title": "Test Campaign",
            "description": "Test description",
            "campaign_type": "invalid_type",
            "budget": "1000",
            "deadline": "2026-03-06T12:00:00Z",
            "target_audience": "Test audience",
            "requirements": "Test requirements",
            "deliverables": "Test deliverables",
            "status": "active"
        }
    }
]

headers = {
    'Authorization': f'Bearer {access_token}',
    'Content-Type': 'application/json'
}

for test_case in test_cases:
    print(f"\n--- Testing: {test_case['name']} ---")
    try:
        response = requests.post(
            'http://localhost:8000/api/collaborations/campaigns/',
            data=json.dumps(test_case['data']),
            headers=headers
        )
        
        print(f"Status Code: {response.status_code}")
        if response.status_code != 201:
            try:
                error_data = response.json()
                print(f"Error: {json.dumps(error_data, indent=2)}")
            except:
                print(f"Error Text: {response.text}")
        else:
            print("Success!")
            
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")