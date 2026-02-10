#!/usr/bin/env python
import os
import django
import requests
import json

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'influencer_platform.settings')
django.setup()

from accounts.models import User
from rest_framework_simplejwt.tokens import RefreshToken

# Get the xyz company user (who owns request ID 3)
company_user = User.objects.get(username='xyz')
print(f"Testing with correct company user: {company_user.username}")

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

try:
    response = requests.put(
        'http://localhost:8000/api/collaborations/requests/3/',
        data=json.dumps(request_data),
        headers=headers
    )
    
    print(f"PUT Status Code: {response.status_code}")
    print(f"PUT Response: {response.text}")
    
    if response.status_code == 200:
        print("Request updated successfully!")
    else:
        print("Request update failed!")
        
except requests.exceptions.RequestException as e:
    print(f"Request failed: {e}")