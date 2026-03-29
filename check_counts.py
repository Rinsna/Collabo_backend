import os
import sys
import django

# Add the current directory to sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'influencer_platform.settings')
django.setup()

from accounts.models import InfluencerProfile
from social_media.models import SocialMediaAccount, FollowerHistory

def check_counts():
    profiles = InfluencerProfile.objects.all()
    print(f"Total Profiles: {profiles.count()}")
    for p in profiles:
        print(f"User: {p.user.username}")
        print(f"  Followers: {p.followers_count}")
        print(f"  Engagement: {p.engagement_rate}")
        print(f"  Latest Preview Views: {p.latest_product_review_views}")
        print(f"  Latest Preview Likes: {p.latest_product_review_likes}")
        
        accounts = p.user.social_accounts.all()
        print(f"  Social Accounts: {accounts.count()}")
        for acc in accounts:
            latest = acc.follower_history.first()
            if latest:
                print(f"    {acc.platform} Latest: Followers={latest.follower_count}, Views={latest.views_count}, Likes={latest.likes_count}")
            else:
                print(f"    {acc.platform}: No history")

if __name__ == "__main__":
    check_counts()
