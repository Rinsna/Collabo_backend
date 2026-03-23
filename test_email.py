import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'influencer_platform.settings')
django.setup()

from accounts.models import User
from accounts.email_service import ApprovalEmailService

print("\n=== EMAIL TEST ===\n")

# Get an approved influencer
user = User.objects.filter(user_type='influencer', approval_status='approved').first()

if user:
    print(f"Testing email for: {user.username} ({user.email})")
    print("\nSending approval email...")
    print("-" * 80)
    
    result = ApprovalEmailService.send_approval_email(user)
    
    print("-" * 80)
    if result:
        print("\n✅ Email sent successfully!")
        print("\nCheck your terminal above to see the email content.")
        print("(Emails are printed to console in development mode)")
    else:
        print("\n❌ Email failed to send")
        print("Check the error logs above")
else:
    print("❌ No approved influencers found to test with")
    print("\nCreate a test influencer first:")
    print("1. Register at /register")
    print("2. Approve in admin dashboard")
    print("3. Run this test again")
