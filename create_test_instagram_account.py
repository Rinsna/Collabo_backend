"""
Create a test Instagram account for testing analytics
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'influencer_platform.settings')
django.setup()

from django.contrib.auth import get_user_model
from social_media.models import SocialMediaAccount, FollowerHistory
from django.utils import timezone
from datetime import timedelta

User = get_user_model()

def create_test_account():
    print("\n" + "="*60)
    print("CREATE TEST INSTAGRAM ACCOUNT")
    print("="*60 + "\n")
    
    # List all influencer users
    influencers = User.objects.filter(user_type='influencer')
    
    if not influencers.exists():
        print("❌ No influencer users found!")
        print("Please create an influencer account first.")
        return
    
    print("Available influencer accounts:\n")
    for i, user in enumerate(influencers, 1):
        print(f"{i}. {user.username} ({user.email})")
    
    print("\nEnter the number of the user you want to add Instagram account to:")
    try:
        choice = int(input("Choice: "))
        user = list(influencers)[choice - 1]
    except (ValueError, IndexError):
        print("❌ Invalid choice!")
        return
    
    print(f"\n✅ Selected user: {user.username} ({user.email})")
    
    # Check if user already has Instagram connected
    existing = SocialMediaAccount.objects.filter(user=user, platform='instagram')
    if existing.exists():
        print(f"\n⚠️  User already has Instagram account connected!")
        print(f"   Username: @{existing.first().username}")
        print(f"   Status: {existing.first().status}")
        
        overwrite = input("\nDo you want to delete and recreate? (yes/no): ")
        if overwrite.lower() == 'yes':
            existing.delete()
            print("✅ Deleted existing account")
        else:
            print("❌ Cancelled")
            return
    
    # Get Instagram username
    instagram_username = input("\nEnter Instagram username (without @): ")
    if not instagram_username:
        instagram_username = f"{user.username}_insta"
    
    # Get follower count
    follower_input = input("Enter follower count (default: 50000): ")
    follower_count = int(follower_input) if follower_input else 50000
    
    # Get engagement rate
    engagement_input = input("Enter engagement rate % (default: 5.5): ")
    engagement_rate = float(engagement_input) if engagement_input else 5.5
    
    print("\n📝 Creating Instagram account...")
    
    # Create Instagram account
    account = SocialMediaAccount.objects.create(
        user=user,
        platform='instagram',
        platform_user_id=f'test_{user.id}',
        username=instagram_username,
        display_name=user.username,
        encrypted_access_token='test_token_encrypted',
        encrypted_refresh_token='',
        token_expires_at=timezone.now() + timedelta(days=60),
        status='active',
        scopes=['user_profile', 'user_media'],
        last_sync=timezone.now(),
        sync_error_count=0,
        last_error=''
    )
    
    print(f"✅ Created Instagram account: @{instagram_username}")
    
    # Create follower history for the last 6 months
    print("\n📊 Creating follower history (last 6 months)...")
    
    base_followers = follower_count - 20000  # Start 20k lower
    
    for i in range(6):
        month_ago = timezone.now() - timedelta(days=30 * (5 - i))
        month_followers = base_followers + (i * 3500)  # Gradual growth
        month_engagement = engagement_rate + (i * 0.1)  # Slight engagement increase
        
        FollowerHistory.objects.create(
            social_account=account,
            follower_count=month_followers,
            following_count=500 + (i * 10),
            posts_count=80 + (i * 5),
            engagement_rate=round(month_engagement, 2),
            likes_count=int(month_followers * month_engagement / 100 * 10),
            comments_count=int(month_followers * month_engagement / 100),
            shares_count=int(month_followers * month_engagement / 100 * 0.5),
            views_count=int(month_followers * 20),
            recorded_at=month_ago
        )
        
        print(f"   Month {i+1}: {month_followers:,} followers, {month_engagement:.1f}% engagement")
    
    # Create current month history
    FollowerHistory.objects.create(
        social_account=account,
        follower_count=follower_count,
        following_count=560,
        posts_count=110,
        engagement_rate=engagement_rate,
        likes_count=int(follower_count * engagement_rate / 100 * 10),
        comments_count=int(follower_count * engagement_rate / 100),
        shares_count=int(follower_count * engagement_rate / 100 * 0.5),
        views_count=int(follower_count * 20),
        recorded_at=timezone.now()
    )
    
    print(f"   Current: {follower_count:,} followers, {engagement_rate:.1f}% engagement")
    
    print("\n" + "="*60)
    print("✅ SUCCESS!")
    print("="*60)
    print(f"\nInstagram account created for {user.username}!")
    print(f"Username: @{instagram_username}")
    print(f"Followers: {follower_count:,}")
    print(f"Engagement: {engagement_rate}%")
    print(f"Status: active")
    print(f"\n🎉 You can now view analytics in the dashboard!")
    print("   The 'No Social Accounts Connected' message should be gone.")
    print("\n")

if __name__ == '__main__':
    create_test_account()
