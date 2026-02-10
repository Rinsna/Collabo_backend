#!/usr/bin/env python
import os
import django
import sys
import time

# Add the project directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'influencer_platform.settings')
django.setup()

from accounts.models import InfluencerProfile, User
from social_media.services import SocialMediaService
import random

def test_realtime_follower_updates():
    print("🚀 Testing Real-time Social Media Follower Updates")
    print("=" * 60)
    
    # Get all influencer profiles with social media handles
    profiles = InfluencerProfile.objects.filter(
        user__is_active=True
    ).exclude(
        instagram_handle='',
        youtube_channel=''
    )
    
    if not profiles.exists():
        print("❌ No influencer profiles with social media handles found!")
        print("Please create some influencer profiles with Instagram/YouTube handles first.")
        return
    
    print(f"📊 Found {profiles.count()} influencer profiles with social media handles")
    print()
    
    for profile in profiles[:3]:  # Test first 3 profiles
        print(f"👤 Testing updates for: {profile.user.username}")
        print(f"   📷 Instagram: {profile.instagram_handle or 'Not set'}")
        print(f"   📺 YouTube: {profile.youtube_channel or 'Not set'}")
        print(f"   👥 Current followers: {profile.followers_count or 0}")
        
        old_followers = profile.followers_count or 0
        
        # Test Instagram update
        if profile.instagram_handle:
            print(f"   🔄 Updating Instagram followers...")
            try:
                instagram_followers = SocialMediaService.get_instagram_followers(profile.instagram_handle)
                if instagram_followers is not None:
                    print(f"   ✅ Instagram: {instagram_followers:,} followers")
                    # Simulate real-time update
                    if 'instagram' in (profile.preferred_platforms or []):
                        profile.followers_count = instagram_followers
                        profile.save()
                        print(f"   📈 Updated profile followers: {old_followers:,} → {instagram_followers:,}")
                else:
                    print(f"   ⚠️ Could not fetch Instagram followers (rate limited or private)")
            except Exception as e:
                print(f"   ❌ Instagram error: {str(e)}")
        
        # Test YouTube update
        if profile.youtube_channel:
            print(f"   🔄 Updating YouTube subscribers...")
            try:
                youtube_subscribers = SocialMediaService.get_youtube_subscribers(profile.youtube_channel)
                if youtube_subscribers is not None:
                    print(f"   ✅ YouTube: {youtube_subscribers:,} subscribers")
                    # Simulate real-time update
                    if 'youtube' in (profile.preferred_platforms or []):
                        if not profile.instagram_handle or 'instagram' not in (profile.preferred_platforms or []):
                            profile.followers_count = youtube_subscribers
                            profile.save()
                            print(f"   📈 Updated profile followers: {old_followers:,} → {youtube_subscribers:,}")
                else:
                    print(f"   ⚠️ Could not fetch YouTube subscribers (API key needed or private)")
            except Exception as e:
                print(f"   ❌ YouTube error: {str(e)}")
        
        print(f"   ⏰ Last updated: {profile.updated_at}")
        print()
        
        # Small delay to avoid rate limiting
        time.sleep(2)
    
    print("🎉 Real-time follower update test completed!")
    print()
    print("💡 Features implemented:")
    print("   ✅ Automatic follower count updates")
    print("   ✅ Instagram integration (using instaloader)")
    print("   ✅ YouTube integration (requires API key)")
    print("   ✅ Real-time profile updates")
    print("   ✅ Platform-specific handling")
    print("   ✅ Error handling and rate limiting")
    print()
    print("🔧 To enable full real-time functionality:")
    print("   1. Start Redis server")
    print("   2. Start Celery worker: celery -A influencer_platform worker")
    print("   3. Start Celery beat: celery -A influencer_platform beat")
    print("   4. Set YouTube API key in .env file")

def simulate_follower_growth():
    """Simulate follower growth for demo purposes"""
    print("\n🎭 Simulating follower growth for demo...")
    
    profiles = InfluencerProfile.objects.filter(user__is_active=True)[:2]
    
    for profile in profiles:
        old_count = profile.followers_count or 0
        # Simulate growth between 1-100 followers
        growth = random.randint(1, 100)
        new_count = old_count + growth
        
        profile.followers_count = new_count
        profile.save()
        
        print(f"📈 {profile.user.username}: {old_count:,} → {new_count:,} (+{growth:,})")
        
        # Simulate real-time notification
        print(f"   🔔 Real-time notification: '{profile.user.username} gained {growth} followers!'")

if __name__ == '__main__':
    test_realtime_follower_updates()
    simulate_follower_growth()