"""
Check social media account connection status
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'influencer_platform.settings')
django.setup()

from django.contrib.auth import get_user_model
from social_media.models import SocialMediaAccount

User = get_user_model()

# Get all users with social media accounts
users_with_accounts = User.objects.filter(social_accounts__isnull=False).distinct()

print("\n" + "="*80)
print("SOCIAL MEDIA ACCOUNT STATUS CHECK")
print("="*80 + "\n")

for user in users_with_accounts:
    print(f"User: {user.username} ({user.user_type})")
    print("-" * 80)
    
    accounts = SocialMediaAccount.objects.filter(user=user)
    
    if not accounts.exists():
        print("  No accounts found")
    else:
        for account in accounts:
            print(f"  Platform: {account.platform}")
            print(f"  Username: @{account.username}")
            print(f"  Status: {account.status}")
            print(f"  Connected: {account.connected_at}")
            print(f"  Last Sync: {account.last_sync or 'Never'}")
            print(f"  Token Expires: {account.token_expires_at or 'N/A'}")
            print(f"  Error Count: {account.sync_error_count}")
            if account.last_error:
                print(f"  Last Error: {account.last_error[:100]}")
            print()
    
    print()

# Summary
total_accounts = SocialMediaAccount.objects.count()
active_accounts = SocialMediaAccount.objects.filter(status='active').count()
expired_accounts = SocialMediaAccount.objects.filter(status='expired').count()
error_accounts = SocialMediaAccount.objects.filter(status='error').count()

print("="*80)
print("SUMMARY")
print("="*80)
print(f"Total Accounts: {total_accounts}")
print(f"Active: {active_accounts}")
print(f"Expired: {expired_accounts}")
print(f"Error: {error_accounts}")
print()
