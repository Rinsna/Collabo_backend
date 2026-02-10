#!/usr/bin/env python
"""Verify API is returning video stats correctly"""
import requests
import json

# Test the API endpoint
url = "http://127.0.0.1:8000/api/auth/influencers/"

try:
    response = requests.get(url, timeout=5)
    
    if response.status_code == 200:
        data = response.json()
        results = data.get('results', [])
        
        print("✓ API Response: 200 OK")
        print(f"✓ Total Influencers: {len(results)}")
        
        # Find profile with video stats
        for profile in results:
            if profile.get('latest_product_review_views') or profile.get('most_viewed_content_views'):
                print(f"\n✓ Found Profile with Stats:")
                print(f"  ID: {profile.get('id')}")
                print(f"  Username: {profile.get('username')}")
                print(f"\n  Latest Product Review:")
                print(f"    Link: {profile.get('latest_product_review_link', 'Not set')}")
                print(f"    Views: {profile.get('latest_product_review_views', 0):,}")
                print(f"    Likes: {profile.get('latest_product_review_likes', 0):,}")
                print(f"\n  Most Viewed Content:")
                print(f"    Link: {profile.get('most_viewed_content_link', 'Not set')}")
                print(f"    Views: {profile.get('most_viewed_content_views', 0):,}")
                print(f"    Likes: {profile.get('most_viewed_content_likes', 0):,}")
                
                # Test formatting
                def format_count(count):
                    if not count or count == 0:
                        return '0'
                    if count >= 1000000:
                        return f"{(count / 1000000):.1f}M"
                    elif count >= 1000:
                        return f"{(count / 1000):.1f}K"
                    return str(count)
                
                print(f"\n  Frontend Display:")
                print(f"    Latest Review Views: {format_count(profile.get('latest_product_review_views', 0))}")
                print(f"    Latest Review Likes: {format_count(profile.get('latest_product_review_likes', 0))}")
                print(f"    Most Viewed Views: {format_count(profile.get('most_viewed_content_views', 0))}")
                print(f"    Most Viewed Likes: {format_count(profile.get('most_viewed_content_likes', 0))}")
                
                break
        else:
            print("\n⚠ No profiles with video stats found")
            print("  Add stats via Profile Edit form")
        
        print("\n✓ API is working correctly!")
        
    else:
        print(f"✗ API Error: {response.status_code}")
        print(response.text)
        
except requests.exceptions.ConnectionError:
    print("✗ Cannot connect to backend server")
    print("  Make sure Django server is running on http://127.0.0.1:8000")
except Exception as e:
    print(f"✗ Error: {e}")
