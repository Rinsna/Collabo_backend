#!/usr/bin/env python
import os
import django
import requests
import json

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'influencer_platform.settings')
django.setup()

# Test login API exactly as frontend would send it
def test_frontend_login():
    url = 'http://localhost:8000/api/auth/login/'
    
    # Test with the exact same format as frontend
    test_data = {
        'email': 'test@test.com',
        'password': 'test123'
    }
    
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }
    
    print("Testing login API (frontend style)...")
    print(f"URL: {url}")
    print(f"Headers: {headers}")
    print(f"Data: {test_data}")
    
    try:
        response = requests.post(url, json=test_data, headers=headers)
        print(f"Status Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
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

    # Also test with wrong password to see the difference
    print("\n" + "="*50)
    print("Testing with wrong password...")
    
    wrong_data = {
        'email': 'test@example.com',
        'password': 'wrongpassword'
    }
    
    try:
        response = requests.post(url, json=wrong_data, headers=headers)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
    except Exception as e:
        print(f"Request failed: {e}")

if __name__ == "__main__":
    test_frontend_login()