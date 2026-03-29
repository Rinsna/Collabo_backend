#!/usr/bin/env python
"""Test script to verify video stats are working"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'influencer_platform.settings')
django.setup()

from accounts.models import InfluencerProfile

# Check if profile 15 exists and has stats
profile = InfluencerProfile.objects.filter(id=15).first()

if profile:
    print(f"✓ Profile ID: {profile.id}")
    print(f"✓ Username: {profile.user.username}")
    print(f"\nLatest Product Review:")
    print(f"  Link: {profile.latest_product_review_link or 'Not set'}")
    print(f"  Views: {profile.latest_product_review_views or 0}")
    print(f"  Likes: {profile.latest_product_review_likes or 0}")
    print(f"\nMost Viewed Content:")
    print(f"  Link: {profile.most_viewed_content_link or 'Not set'}")
    print(f"  Views: {profile.most_viewed_content_views or 0}")
    print(f"  Likes: {profile.most_viewed_content_likes or 0}")
    
    # Test formatting
    def format_count(count):
        if not count or count == 0:
            return '0'
        if count >= 1000000:
            return f"{(count / 1000000):.1f}M"
        elif count >= 1000:
            return f"{(count / 1000):.1f}K"
        return str(count)
    
    print(f"\nFormatted Display:")
    print(f"  Latest Review Views: {format_count(profile.latest_product_review_views)}")
    print(f"  Latest Review Likes: {format_count(profile.latest_product_review_likes)}")
    print(f"  Most Viewed Views: {format_count(profile.most_viewed_content_views)}")
    print(f"  Most Viewed Likes: {format_count(profile.most_viewed_content_likes)}")
else:
    print("✗ Profile ID 15 not found")
    print("\nAvailable profiles:")
    for p in InfluencerProfile.objects.all()[:5]:
        print(f"  - ID {p.id}: {p.user.username}")
