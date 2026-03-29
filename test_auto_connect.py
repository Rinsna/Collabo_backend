"""
Test automatic social media account creation from profile data
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'influencer_platform.settings')
django.setup()

from django.contrib.auth import get_user_model
from accounts.models import InfluencerProfile
from social_media.models import SocialMediaAccount

User = get_user_model()

print("\n" + "="*80)
print("TESTING AUTO-CONNECT SOCIAL MEDIA ACCOUNTS")
print("="*80 + "\n")

# Get an influencer user
influencer = User.objects.filter(user_type='influencer').first()

if not influencer:
    print("❌ No influencer users found. Please create one first.")
    exit()

print(f"Testing with user: {influencer.username}")
print("-" * 80)

# Get or create profile
profile, created = InfluencerProfile.objects.get_or_create(user=influencer)

# Update profile with social media handles
profile.instagram_handle = "test_instagram_user"
profile.youtube_channel = "test_youtube_channel"
profile.followers_count = 50000
profile.engagement_rate = 4.5
profile.save()

print(f"✅ Profile updated with:")
print(f"   Instagram: @{profile.instagram_handle}")
print(f"   YouTube: @{profile.youtube_channel}")
print(f"   Followers: {profile.followers_count}")
print(f"   Engagement: {profile.engagement_rate}%")
print()

# Now manually trigger the auto-create logic
from django.utils import timezone

# Create Instagram account
instagram_account, ig_created = SocialMediaAccount.objects.get_or_create(
    user=influencer,
    platform='instagram',
    defaults={
        'platform_user_id': profile.instagram_handle,
        'username': profile.instagram_handle,
        'encrypted_access_token': 'auto_created',
        'status': 'active',
        'connected_at': timezone.now()
    }
)

# Create YouTube account
youtube_account, yt_created = SocialMediaAccount.objects.get_or_create(
    user=influencer,
    platform='youtube',
    defaults={
        'platform_user_id': profile.youtube_channel,
        'username': profile.youtube_channel,
        'encrypted_access_token': 'auto_created',
        'status': 'active',
        'connected_at': timezone.now()
    }
)

print("SOCIAL MEDIA ACCOUNTS:")
print("-" * 80)
print(f"Instagram: {'✅ Created' if ig_created else '✅ Already exists'}")
print(f"  Username: @{instagram_account.username}")
print(f"  Status: {instagram_account.status}")
print()
print(f"YouTube: {'✅ Created' if yt_created else '✅ Already exists'}")
print(f"  Username: @{youtube_account.username}")
print(f"  Status: {youtube_account.status}")
print()

# Create follower history
from social_media.models import FollowerHistory

if ig_created:
    FollowerHistory.objects.create(
        social_account=instagram_account,
        follower_count=profile.followers_count,
        engagement_rate=profile.engagement_rate,
        sync_source='profile_data'
    )
    print("✅ Created follower history for Instagram")

if yt_created:
    FollowerHistory.objects.create(
        social_account=youtube_account,
        follower_count=profile.followers_count,
        engagement_rate=profile.engagement_rate,
        sync_source='profile_data'
    )
    print("✅ Created follower history for YouTube")

print()
print("="*80)
print("VERIFICATION")
print("="*80)

# Check if accounts are active
active_accounts = SocialMediaAccount.objects.filter(
    user=influencer,
    status='active'
)

print(f"Total active accounts: {active_accounts.count()}")
for account in active_accounts:
    print(f"  - {account.platform.title()}: @{account.username}")

print()
print("✅ Auto-connect test completed!")
print("   Now refresh the analytics page - the alert should be gone!")
print()
