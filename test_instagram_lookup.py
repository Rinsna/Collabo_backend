#!/usr/bin/env python3
"""
Test script for Instagram lookup functionality
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

from django.contrib.auth import get_user_model
from social_media.public_lookup import public_lookup_service
from social_media.instagram_public_api import instagram_public_api

User = get_user_model()

def test_instagram_lookup():
    """Test Instagram lookup functionality"""
    print("Testing Instagram Lookup Functionality")
    print("=" * 50)
    
    # Test usernames to lookup
    test_usernames = ['instagram', 'cristiano', 'selenagomez', 'test_user_not_found']
    
    for username in test_usernames:
        print(f"\nTesting lookup for: @{username}")
        print("-" * 30)
        
        try:
            # Test the public lookup service
            result = public_lookup_service.lookup_instagram_user(username, method='api')
            
            if result:
                print(f"✅ Success!")
                print(f"   Username: @{result['username']}")
                print(f"   Display Name: {result.get('display_name', 'N/A')}")
                print(f"   Followers: {result.get('follower_count', 0):,}")
                print(f"   Following: {result.get('following_count', 0):,}")
                print(f"   Posts: {result.get('posts_count', 0):,}")
                print(f"   Data Source: {result.get('data_source', 'unknown')}")
                print(f"   Method: {result.get('method', 'unknown')}")
                
                if result.get('note'):
                    print(f"   Note: {result['note']}")
                if result.get('warning'):
                    print(f"   Warning: {result['warning']}")
            else:
                print(f"❌ Failed - No data returned")
                
        except Exception as e:
            print(f"❌ Error: {e}")
    
    print("\n" + "=" * 50)
    print("Testing Instagram Public API directly")
    print("=" * 50)
    
    # Test the Instagram public API directly
    for username in ['instagram', 'test_user']:
        print(f"\nTesting direct API for: @{username}")
        print("-" * 30)
        
        try:
            result = instagram_public_api.get_user_data(username)
            
            if result:
                print(f"✅ Success!")
                print(f"   Username: @{result['username']}")
                print(f"   Followers: {result.get('follower_count', 0):,}")
                print(f"   Data Source: {result.get('data_source', 'unknown')}")
                print(f"   Method: {result.get('method', 'unknown')}")
            else:
                print(f"❌ Failed - No data returned")
                
        except Exception as e:
            print(f"❌ Error: {e}")
    
    # Test rate limit status
    print("\n" + "=" * 50)
    print("Rate Limit Status")
    print("=" * 50)
    
    try:
        rate_status = instagram_public_api.get_rate_limit_status()
        print(f"Requests made: {rate_status['requests_made']}")
        print(f"Requests remaining: {rate_status['requests_remaining']}")
        print(f"Rate limit: {rate_status['limit']}")
        print(f"Reset time: {rate_status['reset_time']} seconds")
    except Exception as e:
        print(f"❌ Error getting rate limit status: {e}")

if __name__ == '__main__':
    test_instagram_lookup()