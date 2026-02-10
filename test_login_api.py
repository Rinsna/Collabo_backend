#!/usr/bin/env python
import os
import django
import requests
import json

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'influencer_platform.settings')
django.setup()

# Test login API
def test_login():
    url = 'http://localhost:8000/api/auth/login/'
    
    # Test with existing user
    test_data = {
        'email': 'test@example.com',
        'password': 'testpass123'  # This might not be the correct password
    }
    
    print("Testing login API...")
    print(f"URL: {url}")
    print(f"Data: {test_data}")
    
    try:
        response = requests.post(url, json=test_data, headers={'Content-Type': 'application/json'})
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 400:
            print("400 Bad Request - checking what's wrong...")
            try:
                error_data = response.json()
                print(f"Error details: {error_data}")
            except:
                print("Could not parse error response as JSON")
                
    except Exception as e:
        print(f"Request failed: {e}")

if __name__ == "__main__":
    test_login()