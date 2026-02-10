#!/usr/bin/env python
import os
import django
import requests
import json

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'influencer_platform.settings')
django.setup()

from accounts.models import User
from rest_framework_simplejwt.tokens import RefreshToken

# Get the company user who owns the request
company_user = User.objects.get(username='testcompany')
print(f"Testing with company user: {company_user.username}")

# Generate JWT token
refresh = RefreshToken.for_user(company_user)
access_token = str(refresh.access_token)

# Test accepting collaboration request
request_data = {
    "start_date": "2026-02-10",
    "end_date": "2026-03-10"
}

headers = {
    'Authorization': f'Bearer {access_token}',
    'Content-Type': 'application/json'
}

try:
    response = requests.post(
        'http://localhost:8000/api/collaborations/requests/2/accept/',
        data=json.dumps(request_data),
        headers=headers
    )
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")
    
    if response.status_code == 200:
        print("Request accepted successfully!")
    else:
        print("Request acceptance failed!")
        
except requests.exceptions.RequestException as e:
    print(f"Request failed: {e}")

# Also test if the URL exists by making a GET request (should return 405 Method Not Allowed)
print("\n--- Testing URL existence with GET request ---")
try:
    response = requests.get(
        'http://localhost:8000/api/collaborations/requests/2/accept/',
        headers=headers
    )
    print(f"GET Status Code: {response.status_code}")
    print(f"GET Response: {response.text}")
except requests.exceptions.RequestException as e:
    print(f"GET Request failed: {e}")