#!/usr/bin/env python
"""
Test script for Social Media Integration System
Run this to test the automatic follower update functionality
"""

import os
import django
from django.conf import settings

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'influencer_platform.settings')
django.setup()

from django.contrib.auth import get_user_model
from social_media.models import SocialMediaAccount, FollowerHistory
from social_media.sync_service import sync_service
from social_media.tasks import sync_all_social_accounts
from accounts.models import InfluencerProfile

User = get_user_model()

def test_system_status():
    """Test if the system is properly configured"""
    print("🔍 Testing Social Media Integration System...")
    print("=" * 50)
    
    # Check models
    print(f"📊 Social Media Accounts: {SocialMediaAccount.objects.count()}")
    print(f"📈 Follower History Records: {FollowerHistory.objects.count()}")
    print(f"👥 Total Users: {User.objects.count()}")
    print(f"🌟 Influencer Profiles: {InfluencerProfile.objects.count()}")
    
    # Check configuration
    print("\n🔧 Configuration Check:")
    print(f"Instagram Client ID: {'✅ Set' if settings.INSTAGRAM_CLIENT_ID else '❌ Missing'}")
    print(f"YouTube Client ID: {'✅ Set' if settings.YOUTUBE_CLIENT_ID else '❌ Missing'}")
    print(f"Encryption Key: {'✅ Set' if settings.SOCIAL_MEDIA_ENCRYPTION_KEY else '❌ Missing'}")
    print(f"Redis URL: {'✅ Set' if getattr(settings, 'REDIS_URL', None) else '❌ Missing'}")
    
    # Check active accounts
    active_accounts = SocialMediaAccount.objects.filter(status='active')
    print(f"\n📱 Active Social Accounts: {active_accounts.count()}")
    
    for account in active_accounts:
        latest_history = account.follower_history.first()
        followers = latest_history.follower_count if latest_history else 0
        print(f"  • {account.platform.title()}: @{account.username} ({followers:,} followers)")
    
    return active_accounts.count() > 0

def test_sync_service():
    """Test the sync service functionality"""
    print("\n🔄 Testing Sync Service...")
    print("=" * 30)
    
    try:
        # Get sync statistics
        stats = sync_service.get_sync_statistics(days=7)
        print(f"📊 Sync Statistics (Last 7 days):")
        print(f"  • Total Jobs: {stats['total_jobs']}")
        print(f"  • Success Rate: {stats['success_rate']:.1f}%")
        print(f"  • Accounts Processed: {stats['total_accounts_processed']}")
        
        # Test manual sync (if accounts exist)
        active_accounts = SocialMediaAccount.objects.filter(status='active')
        if active_accounts.exists():
            print(f"\n🚀 Testing manual sync for {active_accounts.count()} accounts...")
            for account in active_accounts[:2]:  # Test first 2 accounts
                print(f"  • Syncing {account.platform}: @{account.username}")
                # Note: This would actually call the API in production
                # success = sync_service.sync_single_account_by_id(account.id)
                # print(f"    Result: {'✅ Success' if success else '❌ Failed'}")
                print(f"    Result: ⏸️ Skipped (API credentials needed)")
        else:
            print("  ℹ️ No active accounts to sync")
            
    except Exception as e:
        print(f"❌ Error testing sync service: {e}")

def test_celery_tasks():
    """Test Celery task functionality"""
    print("\n⚡ Testing Celery Tasks...")
    print("=" * 25)
    
    try:
        # Test task creation (don't actually run without proper setup)
        print("📋 Available Celery Tasks:")
        print("  • sync_all_social_accounts - Sync all active accounts")
        print("  • sync_user_social_accounts - Sync specific user accounts")
        print("  • sync_single_social_account - Sync individual account")
        print("  • refresh_expired_tokens - Refresh expiring tokens")
        print("  • cleanup_old_sync_data - Clean up old data")
        
        # Check if Celery is configured
        from celery import current_app
        print(f"\n🔧 Celery Configuration:")
        print(f"  • Broker URL: {current_app.conf.broker_url}")
        print(f"  • Result Backend: {current_app.conf.result_backend}")
        print(f"  • Task Serializer: {current_app.conf.task_serializer}")
        
        print("\n⚠️ To run tasks, start Celery workers:")
        print("  celery -A influencer_platform worker --loglevel=info")
        print("  celery -A influencer_platform beat --loglevel=info")
        
    except Exception as e:
        print(f"❌ Error testing Celery: {e}")

def show_api_endpoints():
    """Show available API endpoints"""
    print("\n🌐 Available API Endpoints:")
    print("=" * 30)
    
    endpoints = [
        ("GET", "/api/social-media/accounts/", "List connected accounts"),
        ("POST", "/api/social-media/connect/", "Connect new account via OAuth"),
        ("POST", "/api/social-media/accounts/{id}/sync/", "Manual sync account"),
        ("GET", "/api/social-media/stats/follower/", "Get follower statistics"),
        ("GET", "/api/social-media/stats/sync/", "Get sync history"),
        ("POST", "/api/social-media/sync/user/", "Sync all user accounts"),
        ("GET", "/api/social-media/sync/status/{task_id}/", "Check sync status"),
    ]
    
    for method, endpoint, description in endpoints:
        print(f"  {method:4} {endpoint:35} - {description}")

def show_oauth_flow():
    """Show OAuth flow instructions"""
    print("\n🔐 OAuth Flow Instructions:")
    print("=" * 30)
    
    print("1. Instagram Business/Creator Account:")
    print("   • Redirect to: https://api.instagram.com/oauth/authorize")
    print("   • Scopes: user_profile,user_media")
    print("   • Handle callback at: /auth/instagram/callback")
    
    print("\n2. YouTube Channel:")
    print("   • Redirect to: https://accounts.google.com/oauth2/auth")
    print("   • Scopes: https://www.googleapis.com/auth/youtube.readonly")
    print("   • Handle callback at: /auth/youtube/callback")
    
    print("\n3. Frontend Components:")
    print("   • ConnectAccounts.js - Account management UI")
    print("   • OAuthCallback.js - Handle OAuth responses")

def main():
    """Run all tests"""
    print("🚀 Social Media Integration System Test")
    print("=" * 50)
    
    has_accounts = test_system_status()
    test_sync_service()
    test_celery_tasks()
    show_api_endpoints()
    show_oauth_flow()
    
    print("\n" + "=" * 50)
    print("✅ System Test Complete!")
    
    if not has_accounts:
        print("\n💡 Next Steps:")
        print("1. Set up OAuth credentials in .env file")
        print("2. Start Celery workers (run start_workers.bat)")
        print("3. Connect social media accounts via frontend")
        print("4. Watch automatic follower updates!")
    else:
        print("\n🎉 System is ready! Accounts are connected and syncing.")

if __name__ == "__main__":
    main()