import os
import django
import sys
from django.utils import timezone

# Add the project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'influencer_platform.settings')
django.setup()

from accounts.models import User, InfluencerProfile

def seed_influencers():
    print("Seeding Influencers...")
    
    influencers_data = [
        {
            "username": "sarah_style",
            "first_name": "Sarah",
            "last_name": "Johnson",
            "email": "sarah@example.com",
            "bio": "Minimalist fashion lover and lifestyle creator based in NYC. Sharing daily outfits and aesthetic inspiration.",
            "category": "fashion",
            "followers_count": 125000,
            "engagement_rate": 4.2,
            "image_url": "https://images.unsplash.com/photo-1494790108377-be9c29b29330?w=400&h=400&fit=crop"
        },
        {
            "username": "tech_tom",
            "first_name": "Tom",
            "last_name": "Chen",
            "email": "tom@example.com",
            "bio": "Reviewing the latest gadgets and setup inspiration. Building the future of desk setups.",
            "category": "tech",
            "followers_count": 85000,
            "engagement_rate": 5.8,
            "image_url": "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=400&h=400&fit=crop"
        },
        {
            "username": "wander_with_mia",
            "first_name": "Mia",
            "last_name": "Wong",
            "email": "mia@example.com",
            "bio": "Exploring hidden gems around the world. Travel tips, hotel reviews, and cultural insights.",
            "category": "travel",
            "followers_count": 250000,
            "engagement_rate": 3.1,
            "image_url": "https://images.unsplash.com/photo-1524504388940-b1c1722653e1?w=400&h=400&fit=crop"
        },
        {
            "username": "fitness_flex",
            "first_name": "Alex",
            "last_name": "Rivera",
            "email": "alex@example.com",
            "bio": "Certified personal trainer. Helping you reach your fitness goals with sustainable habits.",
            "category": "fitness",
            "followers_count": 50000,
            "engagement_rate": 7.5,
            "image_url": "https://images.unsplash.com/photo-1544005313-94ddf0286df2?w=400&h=400&fit=crop"
        },
        {
            "username": "chef_clara",
            "first_name": "Clara",
            "last_name": "Smith",
            "email": "clara@example.com",
            "bio": "Easy plant-based recipes for a healthier life. Cooking should be fun and simple!",
            "category": "lifestyle",
            "followers_count": 15000,
            "engagement_rate": 12.0,
            "image_url": "https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=400&h=400&fit=crop"
        }
    ]

    for data in influencers_data:
        # Check by email
        user, created = User.objects.get_or_create(
            email=data["email"],
            defaults={
                "username": data["username"],
                "first_name": data["first_name"],
                "last_name": data["last_name"],
                "user_type": 'influencer'
            }
        )
        
        if created:
            user.set_password("password123")
            print(f"Created influencer user: {data['username']}")
        
        # Ensure profile exists and is updated
        profile, p_created = InfluencerProfile.objects.update_or_create(
            user=user,
            defaults={
                "bio": data["bio"],
                "category": data["category"],
                "followers_count": data["followers_count"],
                "engagement_rate": data["engagement_rate"],
                "profile_image": data["image_url"]
            }
        )
        
        # Always FORCIBLY APPROVE
        user.is_approved = True
        user.approval_status = 'approved'
        if not user.approved_at:
            user.approved_at = timezone.now()
        user.save()
        
        print(f"Verified & Approved: {user.username}")

    print("Success: Influencer Directory is now populated and LIVE!")

if __name__ == "__main__":
    seed_influencers()
