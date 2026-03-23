import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'influencer_platform.settings')
django.setup()

from accounts.models import User
from accounts.email_service import ApprovalEmailService

# Find a pending influencer
pending_influencers = User.objects.filter(
    user_type='influencer',
    approval_status='pending'
)

if pending_influencers.exists():
    influencer = pending_influencers.first()
    print(f"\n{'='*60}")
    print(f"Testing email for: {influencer.username} ({influencer.email})")
    print(f"{'='*60}\n")
    
    # Send approval email
    ApprovalEmailService.send_approval_email(influencer)
    
    print(f"\n{'='*60}")
    print("Email sent! Check the output above in the terminal.")
    print(f"{'='*60}\n")
else:
    print("\nNo pending influencers found.")
    print("Creating a test pending influencer...\n")
    
    # Create a test user
    test_user = User.objects.create_user(
        username='test_influencer_email',
        email='testinfluencer@example.com',
        password='testpass123',
        user_type='influencer',
        approval_status='pending'
    )
    
    print(f"Created test user: {test_user.username}")
    print(f"Sending approval email...\n")
    
    ApprovalEmailService.send_approval_email(test_user)
    
    print(f"\n{'='*60}")
    print("Email sent! Check the output above in the terminal.")
    print(f"{'='*60}\n")
