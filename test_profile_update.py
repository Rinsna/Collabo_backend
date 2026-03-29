"""
Test script to verify profile update works without TikTok/Twitter fields
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'influencer_platform.settings')
django.setup()

from accounts.models import User, InfluencerProfile
from accounts.serializers import InfluencerProfileSerializer

def test_profile_update():
    print("Testing Profile Update Without TikTok/Twitter...")
    print("=" * 60)
    
    # Get an influencer user
    influencer_user = User.objects.filter(user_type='influencer').first()
    
    if not influencer_user:
        print("❌ No influencer user found.")
        return
    
    profile = InfluencerProfile.objects.get(user=influencer_user)
    print(f"✅ Found profile: {profile.user.username}")
    
    # Test data without TikTok/Twitter
    test_data = {
        'bio': 'Updated bio without TikTok/Twitter',
        'category': 'tech',
        'instagram_handle': '@test_instagram',
        'youtube_channel': 'TestChannel',
        'rate_per_post': 10000.00,
        'rate_per_story': 5000.00,
        'rate_per_reel': 8000.00,
        'rate_per_video': 15000.00,
        'location': 'Delhi, India',
        'languages': ['English', 'Hindi'],
        'website_url': 'https://example.com'
    }
    
    print("\n📝 Updating profile with test data...")
    serializer = InfluencerProfileSerializer(profile, data=test_data, partial=True)
    
    if serializer.is_valid():
        serializer.save()
        print("✅ Profile updated successfully!")
        print("\nUpdated fields:")
        for key, value in test_data.items():
            print(f"  - {key}: {value}")
    else:
        print("❌ Validation errors:")
        for field, errors in serializer.errors.items():
            print(f"  - {field}: {errors}")
        return
    
    # Verify the update
    print("\n🔍 Verifying update...")
    profile.refresh_from_db()
    
    checks = [
        ('bio', test_data['bio']),
        ('category', test_data['category']),
        ('instagram_handle', test_data['instagram_handle']),
        ('youtube_channel', test_data['youtube_channel']),
        ('location', test_data['location']),
    ]
    
    all_good = True
    for field, expected in checks:
        actual = getattr(profile, field)
        if actual == expected:
            print(f"  ✅ {field}: {actual}")
        else:
            print(f"  ❌ {field}: Expected '{expected}', got '{actual}'")
            all_good = False
    
    # Verify TikTok/Twitter fields don't exist
    print("\n🔍 Verifying TikTok/Twitter fields removed...")
    if not hasattr(profile, 'tiktok_handle'):
        print("  ✅ tiktok_handle field removed")
    else:
        print("  ❌ tiktok_handle field still exists")
        all_good = False
    
    if not hasattr(profile, 'twitter_handle'):
        print("  ✅ twitter_handle field removed")
    else:
        print("  ❌ twitter_handle field still exists")
        all_good = False
    
    print("\n" + "=" * 60)
    if all_good:
        print("✅ All tests passed!")
    else:
        print("❌ Some tests failed!")

if __name__ == '__main__':
    test_profile_update()
