import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'influencer_platform.settings')
django.setup()

from accounts.models import User
from django.utils import timezone

# Fix all approved influencers that have is_approved=False
influencers = User.objects.filter(
    user_type='influencer',
    approval_status='approved',
    is_approved=False
)

print(f"\nFound {influencers.count()} influencers with approval_status='approved' but is_approved=False")
print("\nFixing...")

for user in influencers:
    user.is_approved = True
    if not user.approved_at:
        user.approved_at = timezone.now()
    user.save()
    print(f"✅ Fixed: {user.username} ({user.email})")

print(f"\n✅ Fixed {influencers.count()} influencers!")
print("\nAll approved influencers can now login.")
