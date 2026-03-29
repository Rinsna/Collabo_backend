import os
import sys
import django
from pathlib import Path

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'influencer_platform.settings')
django.setup()

from accounts.models import User, InfluencerProfile
from django.utils import timezone

def approve_all():
    influencers = User.objects.filter(user_type='influencer')
    print(f"Found {influencers.count()} influencers.")
    
    for user in influencers:
        user.is_approved = True
        user.approval_status = 'approved'
        if not user.approved_at:
            user.approved_at = timezone.now()
        user.save()
        
        # Ensure profile exists
        InfluencerProfile.objects.get_or_create(user=user)
        print(f"Approved: {user.username} ({user.email})")

if __name__ == '__main__':
    approve_all()
