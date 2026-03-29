import os
import sys
import django

# Add the current directory to sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'influencer_platform.settings')
django.setup()

from accounts.models import InfluencerProfile
from social_media.models import SocialMediaAccount, FollowerHistory
from social_media.sync_service import sync_service

def force_update_profiles():
    profiles = InfluencerProfile.objects.all()
    print(f"Updating {profiles.count()} profiles from existing history...")
    for p in profiles:
        print(f"Updating @{p.user.username}...")
        sync_service._update_influencer_profile(p)
        p.refresh_from_db()
        print(f"  Result: Followers={p.followers_count}, Views={p.latest_product_review_views}, Likes={p.latest_product_review_likes}")

if __name__ == "__main__":
    force_update_profiles()
