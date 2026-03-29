#!/usr/bin/env python3
"""
Simple test script for Instagram lookup functionality without Redis
"""

import os
import sys
import django
from django.conf import settings

# Add the backend directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'influencer_platform.settings')
django.setup()

# Override cache settings to use dummy cache for testing
from django.core.cache import cache
from django.core.cache.backends.dummy import DummyCache

def test_instagram_api_direct():
    """Test Instagram API functionality directly without cache"""
    print("Testing Instagram API Direct (No Cache)")
    print("=" * 50)
    
    from social_media.instagram_public_api import InstagramPublicAPI
    
    # Create API instance
    api = InstagramPublicAPI()
    
    # Test usernames
    test_usernames = ['instagram', 'test_user']
    
    for username in test_usernames:
        print(f"\nTesting: @{username}")
        print("-" * 20)
        
        try:
            # Test the fallback data method (should always work)
            fallback_data = api._get_fallback_data(username)
            print(f"✅ Fallback data generated:")
            print(f"   Username: @{fallback_data['username']}")
            print(f"   Display Name: {fallback_data['display_name']}")
            print(f"   Followers: {fallback_data['follower_count']:,}")
            print(f"   Data Source: {fallback_data['data_source']}")
            print(f"   Method: {fallback_data['method']}")
            
            if fallback_data.get('note'):
                print(f"   Note: {fallback_data['note']}")
                
        except Exception as e:
            print(f"❌ Error: {e}")

def test_public_lookup_service():
    """Test public lookup service with mock data"""
    print("\n" + "=" * 50)
    print("Testing Public Lookup Service")
    print("=" * 50)
    
    from social_media.public_lookup import SocialMediaPublicLookup
    
    # Create service instance
    service = SocialMediaPublicLookup()
    
    test_usernames = ['instagram', 'test_user']
    
    for username in test_usernames:
        print(f"\nTesting: @{username}")
        print("-" * 20)
        
        try:
            # This should return mock/fallback data
            result = service.lookup_instagram_user(username, method='api')
            
            if result:
                print(f"✅ Success!")
                print(f"   Username: @{result['username']}")
                print(f"   Display Name: {result.get('display_name', 'N/A')}")
                print(f"   Followers: {result.get('follower_count', 0):,}")
                print(f"   Data Source: {result.get('data_source', 'unknown')}")
                
                if result.get('note'):
                    print(f"   Note: {result['note']}")
            else:
                print(f"❌ No data returned")
                
        except Exception as e:
            print(f"❌ Error: {e}")

def test_api_endpoint_simulation():
    """Simulate API endpoint call"""
    print("\n" + "=" * 50)
    print("Simulating API Endpoint Call")
    print("=" * 50)
    
    # Simulate what the API endpoint would do
    from social_media.public_lookup import public_lookup_service
    
    username = 'test_user'
    method = 'api'
    
    print(f"Simulating POST /api/social-media/lookup/instagram/")
    print(f"Request data: {{'username': '{username}', 'method': '{method}'}}")
    
    try:
        user_data = public_lookup_service.lookup_instagram_user(username, method)
        
        if user_data:
            response_data = {
                'success': True,
                'data': user_data,
                'username': username,
                'method_used': method
            }
            print(f"✅ API Response:")
            print(f"   Success: {response_data['success']}")
            print(f"   Username: @{response_data['username']}")
            print(f"   Method Used: {response_data['method_used']}")
            print(f"   Data: {response_data['data']}")
        else:
            response_data = {
                'success': False,
                'error': 'User not found or unable to fetch data',
                'username': username
            }
            print(f"❌ API Response:")
            print(f"   Success: {response_data['success']}")
            print(f"   Error: {response_data['error']}")
            
    except Exception as e:
        response_data = {
            'success': False,
            'error': 'Lookup service temporarily unavailable',
            'username': username
        }
        print(f"❌ API Response (Exception):")
        print(f"   Success: {response_data['success']}")
        print(f"   Error: {response_data['error']}")
        print(f"   Exception: {e}")

if __name__ == '__main__':
    test_instagram_api_direct()
    test_public_lookup_service()
    test_api_endpoint_simulation()