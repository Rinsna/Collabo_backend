#!/usr/bin/env python3
"""
Test the Instagram lookup API endpoint
"""

import requests
import json
from django.contrib.auth import get_user_model
from django.test import Client
from django.urls import reverse
import os
import sys
import django

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'influencer_platform.settings')
django.setup()

User = get_user_model()

def test_api_endpoint_with_auth():
    """Test the API endpoint with proper authentication"""
    print("Testing Instagram Lookup API Endpoint")
    print("=" * 50)
    
    # Create a test user if it doesn't exist
    try:
        user = User.objects.get(email='test@test.com')
        print(f"Using existing test user: {user.email}")
    except User.DoesNotExist:
        print("Test user not found. Please run the application first to create test users.")
        return
    
    # Use Django test client for authenticated requests
    client = Client()
    
    # Login the user
    login_success = client.login(email='test@test.com', password='test123')
    if not login_success:
        print("❌ Failed to login test user")
        return
    
    print("✅ Successfully logged in test user")
    
    # Test the Instagram lookup endpoint
    test_usernames = ['instagram', 'test_user', 'cristiano']
    
    for username in test_usernames:
        print(f"\nTesting lookup for: @{username}")
        print("-" * 30)
        
        try:
            response = client.post(
                '/api/social-media/lookup/instagram/',
                data=json.dumps({
                    'username': username,
                    'method': 'api'
                }),
                content_type='application/json'
            )
            
            print(f"Status Code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Success!")
                print(f"   Response: {json.dumps(data, indent=2)}")
            else:
                print(f"❌ Failed with status {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"   Error: {json.dumps(error_data, indent=2)}")
                except:
                    print(f"   Raw response: {response.content}")
                    
        except Exception as e:
            print(f"❌ Exception: {e}")

def test_direct_http_request():
    """Test with direct HTTP request to running server"""
    print("\n" + "=" * 50)
    print("Testing Direct HTTP Request (if server is running)")
    print("=" * 50)
    
    # First, try to get a session/token by logging in
    try:
        # Try to login and get session
        login_response = requests.post(
            'http://localhost:8000/api/auth/login/',
            json={
                'email': 'test@test.com',
                'password': 'test123'
            },
            timeout=10
        )
        
        if login_response.status_code == 200:
            login_data = login_response.json()
            token = login_data.get('access')
            
            if token:
                print("✅ Successfully obtained access token")
                
                # Test Instagram lookup with token
                headers = {
                    'Authorization': f'Bearer {token}',
                    'Content-Type': 'application/json'
                }
                
                test_data = {
                    'username': 'test_user',
                    'method': 'api'
                }
                
                lookup_response = requests.post(
                    'http://localhost:8000/api/social-media/lookup/instagram/',
                    json=test_data,
                    headers=headers,
                    timeout=10
                )
                
                print(f"Lookup Status Code: {lookup_response.status_code}")
                
                if lookup_response.status_code == 200:
                    data = lookup_response.json()
                    print(f"✅ Instagram Lookup Success!")
                    print(f"   Response: {json.dumps(data, indent=2)}")
                else:
                    print(f"❌ Instagram Lookup Failed")
                    try:
                        error_data = lookup_response.json()
                        print(f"   Error: {json.dumps(error_data, indent=2)}")
                    except:
                        print(f"   Raw response: {lookup_response.content}")
            else:
                print("❌ No access token in login response")
                print(f"   Login response: {json.dumps(login_data, indent=2)}")
        else:
            print(f"❌ Login failed with status {login_response.status_code}")
            try:
                error_data = login_response.json()
                print(f"   Login error: {json.dumps(error_data, indent=2)}")
            except:
                print(f"   Raw login response: {login_response.content}")
                
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to server. Make sure Django server is running on localhost:8000")
    except Exception as e:
        print(f"❌ Exception during HTTP test: {e}")

if __name__ == '__main__':
    test_api_endpoint_with_auth()
    test_direct_http_request()