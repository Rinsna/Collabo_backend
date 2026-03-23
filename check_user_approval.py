import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'influencer_platform.settings')
django.setup()

from accounts.models import User

# Get all influencers
influencers = User.objects.filter(user_type='influencer')

print("\n=== INFLUENCER APPROVAL STATUS ===\n")
for user in influencers:
    print(f"ID: {user.id}")
    print(f"Username: {user.username}")
    print(f"Email: {user.email}")
    print(f"is_approved: {user.is_approved}")
    print(f"approval_status: {user.approval_status}")
    print(f"is_active: {user.is_active}")
    print(f"approved_at: {user.approved_at}")
    print(f"approved_by: {user.approved_by}")
    print("-" * 50)

print(f"\nTotal influencers: {influencers.count()}")
print(f"Approved: {influencers.filter(approval_status='approved').count()}")
print(f"Pending: {influencers.filter(approval_status='pending').count()}")
print(f"Rejected: {influencers.filter(approval_status='rejected').count()}")
