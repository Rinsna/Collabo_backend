import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'influencer_platform.settings')
django.setup()

from accounts.models import User
from accounts.serializers import UserSerializer

# Get a test influencer
influencer = User.objects.filter(user_type='influencer').first()

if influencer:
    print(f"\n{'='*60}")
    print(f"Testing User: {influencer.username}")
    print(f"{'='*60}\n")
    
    print("Direct Model Fields:")
    print(f"  approval_status: {influencer.approval_status}")
    print(f"  is_approved: {influencer.is_approved}")
    print(f"  approval_shown: {influencer.approval_shown}")
    print(f"  rejection_reason: {influencer.rejection_reason}")
    
    print("\nSerialized Data:")
    serializer = UserSerializer(influencer)
    data = serializer.data
    print(f"  approval_status: {data.get('approval_status')}")
    print(f"  is_approved: {data.get('is_approved')}")
    print(f"  approval_shown: {data.get('approval_shown')}")
    print(f"  rejection_reason: {data.get('rejection_reason')}")
    
    print(f"\n{'='*60}\n")
else:
    print("No influencer found in database")
