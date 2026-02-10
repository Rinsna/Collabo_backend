"""
Test script to verify new influencer profile fields
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'influencer_platform.settings')
django.setup()

from accounts.models import User, InfluencerProfile
from accounts.serializers import InfluencerProfileSerializer

def test_profile_fields():
    print("Testing Influencer Profile Fields...")
    print("=" * 60)
    
    # Get an influencer user
    influencer_user = User.objects.filter(user_type='influencer').first()
    
    if not influencer_user:
        print("❌ No influencer user found. Please create one first.")
        return
    
    profile, created = InfluencerProfile.objects.get_or_create(user=influencer_user)
    
    print(f"\n✅ Found influencer: {influencer_user.username}")
    print(f"   Profile ID: {profile.id}")
    
    # Test updating new fields
    print("\n📝 Testing new fields update...")
    
    profile.rate_per_story = 5000.00
    profile.rate_per_reel = 8000.00
    profile.rate_per_video = 15000.00
    profile.tiktok_handle = "@test_influencer"
    profile.twitter_handle = "@test_influencer"
    profile.profile_image = "https://example.com/profile.jpg"
    profile.portfolio_images = [
        "https://example.com/portfolio1.jpg",
        "https://example.com/portfolio2.jpg"
    ]
    profile.portfolio_videos = [
        "https://youtube.com/watch?v=example1",
        "https://youtube.com/watch?v=example2"
    ]
    profile.website_url = "https://example.com"
    profile.location = "Mumbai, India"
    profile.languages = ["English", "Hindi", "Marathi"]
    
    profile.save()
    print("✅ Profile updated successfully!")
    
    # Verify serializer includes all fields
    print("\n🔍 Verifying serializer output...")
    serializer = InfluencerProfileSerializer(profile)
    data = serializer.data
    
    new_fields = [
        'rate_per_story', 'rate_per_reel', 'rate_per_video',
        'tiktok_handle', 'twitter_handle', 'profile_image',
        'portfolio_images', 'portfolio_videos', 'website_url',
        'location', 'languages'
    ]
    
    print("\nNew Fields in Serializer:")
    for field in new_fields:
        if field in data:
            print(f"  ✅ {field}: {data[field]}")
        else:
            print(f"  ❌ {field}: NOT FOUND")
    
    print("\n" + "=" * 60)
    print("✅ All tests completed!")
    print("\nProfile Summary:")
    print(f"  - Rates: Post=₹{profile.rate_per_post}, Story=₹{profile.rate_per_story}, "
          f"Reel=₹{profile.rate_per_reel}, Video=₹{profile.rate_per_video}")
    print(f"  - Social: Instagram={profile.instagram_handle}, TikTok={profile.tiktok_handle}, "
          f"Twitter={profile.twitter_handle}")
    print(f"  - Portfolio: {len(profile.portfolio_images)} images, {len(profile.portfolio_videos)} videos")
    print(f"  - Location: {profile.location}")
    print(f"  - Languages: {', '.join(profile.languages)}")
    print(f"  - Website: {profile.website_url}")

if __name__ == '__main__':
    test_profile_fields()
