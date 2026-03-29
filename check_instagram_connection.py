"""
Debug script to check Instagram connection status
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'influencer_platform.settings')
django.setup()

from django.contrib.auth import get_user_model
from social_media.models import SocialMediaAccount, FollowerHistory

User = get_user_model()

def check_connections():
    print("\n" + "="*60)
    print("INSTAGRAM CONNECTION STATUS CHECK")
    print("="*60 + "\n")
    
    # Get all influencer users
    influencers = User.objects.filter(user_type='influencer')
    
    for user in influencers:
        print(f"\n👤 User: {user.username} ({user.email})")
        print("-" * 60)
        
        # Check social media accounts
        accounts = SocialMediaAccount.objects.filter(user=user)
        
        if not accounts.exists():
            print("   ❌ No social media accounts connected")
            continue
        
        for account in accounts:
            print(f"\n   📱 Platform: {account.platform.upper()}")
            print(f"   Username: @{account.username}")
            print(f"   Status: {account.status}")
            print(f"   Connected: {account.connected_at}")
            print(f"   Last Sync: {account.last_sync or 'Never'}")
            print(f"   Error Count: {account.sync_error_count}")
            
            if account.last_error:
                print(f"   ⚠️  Last Error: {account.last_error}")
            
            # Check follower history
            history_count = account.follower_history.count()
            print(f"   📊 History Records: {history_count}")
            
            if history_count > 0:
                latest = account.follower_history.first()
                print(f"   👥 Latest Followers: {latest.follower_count:,}")
                print(f"   💚 Engagement Rate: {latest.engagement_rate}%")
                print(f"   📅 Recorded: {latest.recorded_at}")
            else:
                print("   ⚠️  No follower history data yet")
            
            # Check if account would be picked up by analytics
            if account.status == 'active':
                print("   ✅ Account is ACTIVE - will show in analytics")
            else:
                print(f"   ❌ Account status is '{account.status}' - will NOT show in analytics")
    
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    
    total_accounts = SocialMediaAccount.objects.count()
    active_accounts = SocialMediaAccount.objects.filter(status='active').count()
    error_accounts = SocialMediaAccount.objects.filter(status='error').count()
    
    print(f"\nTotal Accounts: {total_accounts}")
    print(f"Active Accounts: {active_accounts}")
    print(f"Error Accounts: {error_accounts}")
    
    if active_accounts == 0:
        print("\n⚠️  WARNING: No active accounts found!")
        print("This is why analytics shows 'No Social Accounts Connected'")
        print("\nPossible fixes:")
        print("1. Reconnect your Instagram account")
        print("2. Check if sync failed and fix the errors")
        print("3. Manually set account status to 'active' in database")
    
    print("\n")

if __name__ == '__main__':
    check_connections()
