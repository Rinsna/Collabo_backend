"""
Create test social media accounts for existing users
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'influencer_platform.settings')
django.setup()

from django.contrib.auth import get_user_model
from accounts.models import InfluencerProfile
from social_media.models import SocialMediaAccount, FollowerHistory
from django.utils import timezone

User = get_user_model()

print("\n" + "="*80)
print("CREATE TEST SOCIAL MEDIA ACCOUNTS")
print("="*80 + "\n")

# Get all influencer users
influencers = User.objects.filter(user_type='influencer')

if not influencers.exists():
    print("❌ No influencer users found.")
    exit()

for user in influencers:
    print(f"Processing: {user.username}")
    print("-" * 80)
    
    # Get profile
    try:
        profile = InfluencerProfile.objects.get(user=user)
    except InfluencerProfile.DoesNotExist:
        print(f"  ⚠️  No profile found, skipping")
        continue
    
    created_accounts = []
    
    # Create Instagram account if handle exists
    if profile.instagram_handle:
        instagram_handle = profile.instagram_handle.strip().lstrip('@')
        account, created = SocialMediaAccount.objects.get_or_create(
            user=user,
            platform='instagram',
            defaults={
                'platform_user_id': instagram_handle,
                'username': instagram_handle,
                'encrypted_access_token': 'auto_created',
                'status': 'active',
                'connected_at': timezone.now()
            }
        )
        
        if created:
            created_accounts.append('Instagram')
            # Create follower history
            if profile.followers_count:
                FollowerHistory.objects.create(
                    social_account=account,
                    follower_count=profile.followers_count,
                    engagement_rate=profile.engagement_rate or 0,
                    sync_source='profile_data'
                )
            print(f"  ✅ Created Instagram account: @{instagram_handle}")
        else:
            print(f"  ℹ️  Instagram account already exists: @{instagram_handle}")
    
    # Create YouTube account if channel exists
    if profile.youtube_channel:
        youtube_channel = profile.youtube_channel.strip().lstrip('@')
        account, created = SocialMediaAccount.objects.get_or_create(
            user=user,
            platform='youtube',
            defaults={
                'platform_user_id': youtube_channel,
                'username': youtube_channel,
                'encrypted_access_token': 'auto_created',
                'status': 'active',
                'connected_at': timezone.now()
            }
        )
        
        if created:
            created_accounts.append('YouTube')
            # Create follower history
            if profile.followers_count:
                FollowerHistory.objects.create(
                    social_account=account,
                    follower_count=profile.followers_count,
                    engagement_rate=profile.engagement_rate or 0,
                    sync_source='profile_data'
                )
            print(f"  ✅ Created YouTube account: @{youtube_channel}")
        else:
            print(f"  ℹ️  YouTube account already exists: @{youtube_channel}")
    
    if not created_accounts and not profile.instagram_handle and not profile.youtube_channel:
        print(f"  ⚠️  No social media handles in profile")
    
    print()

# Summary
print("="*80)
print("SUMMARY")
print("="*80)

total_accounts = SocialMediaAccount.objects.count()
active_accounts = SocialMediaAccount.objects.filter(status='active').count()

print(f"Total Social Media Accounts: {total_accounts}")
print(f"Active Accounts: {active_accounts}")
print()

# Show all accounts
if total_accounts > 0:
    print("All Connected Accounts:")
    print("-" * 80)
    for account in SocialMediaAccount.objects.all():
        print(f"  {account.user.username} - {account.platform.title()}: @{account.username} ({account.status})")
    print()

print("✅ Done! Refresh your analytics page to see the changes.")
print()
