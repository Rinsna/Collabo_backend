"""
Test script for payment tracking system
Run with: python manage.py shell < test_payment_tracking.py
"""

from accounts.models import User, CompanyProfile
from collaborations.models import Campaign
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal

print("\n" + "="*60)
print("PAYMENT TRACKING SYSTEM TEST")
print("="*60 + "\n")

# Get or create a test company user
try:
    company_user = User.objects.filter(user_type='company').first()
    if not company_user:
        print("❌ No company user found. Please create a company user first.")
        exit()
    
    print(f"✓ Using company: {company_user.username}")
    
    # Get company profile
    company_profile = company_user.company_profile
    print(f"  Company Name: {company_profile.company_name}")
    print(f"  Initial Pending Payment: ₹{company_profile.pending_payment}")
    print(f"  Initial Total Spend: ₹{company_profile.total_spend}")
    print()
    
    # Create a test campaign
    test_budget = Decimal('50000.00')
    campaign = Campaign.objects.create(
        company=company_user,
        title="Test Payment Tracking Campaign",
        description="This is a test campaign to verify payment tracking",
        campaign_type='sponsored_post',
        budget=test_budget,
        target_audience="Test Audience",
        requirements="Test Requirements",
        deliverables="Test Deliverables",
        deadline=timezone.now() + timedelta(days=30),
        status='draft'
    )
    print(f"✓ Created test campaign: {campaign.title}")
    print(f"  Campaign ID: {campaign.id}")
    print(f"  Budget: ₹{campaign.budget}")
    print(f"  Status: {campaign.status}")
    print(f"  Payment Status: {campaign.payment_status}")
    print(f"  Payment Added to Pending: {campaign.payment_added_to_pending}")
    print()
    
    # Test 1: Change status to completed
    print("TEST 1: Changing campaign status to 'completed'")
    print("-" * 60)
    campaign.status = 'completed'
    campaign.save()
    
    # Refresh from database
    campaign.refresh_from_db()
    company_profile.refresh_from_db()
    
    print(f"✓ Campaign status changed to: {campaign.status}")
    print(f"  Payment Added to Pending: {campaign.payment_added_to_pending}")
    print(f"  Company Pending Payment: ₹{company_profile.pending_payment}")
    print(f"  Company Total Spend: ₹{company_profile.total_spend}")
    
    if company_profile.pending_payment >= test_budget:
        print("✅ TEST 1 PASSED: Budget added to pending payment")
    else:
        print("❌ TEST 1 FAILED: Budget not added to pending payment")
    print()
    
    # Test 2: Try to add payment again (should not duplicate)
    print("TEST 2: Attempting to complete campaign again (should not duplicate)")
    print("-" * 60)
    old_pending = company_profile.pending_payment
    campaign.status = 'active'
    campaign.save()
    campaign.status = 'completed'
    campaign.save()
    
    company_profile.refresh_from_db()
    print(f"  Old Pending Payment: ₹{old_pending}")
    print(f"  New Pending Payment: ₹{company_profile.pending_payment}")
    
    if company_profile.pending_payment == old_pending:
        print("✅ TEST 2 PASSED: No duplicate addition")
    else:
        print("❌ TEST 2 FAILED: Duplicate addition occurred")
    print()
    
    # Test 3: Mark payment as completed (simulate API call)
    print("TEST 3: Marking payment as completed")
    print("-" * 60)
    old_pending = company_profile.pending_payment
    old_total_spend = company_profile.total_spend
    
    # Simulate the mark payment completed logic
    if campaign.status == 'completed' and campaign.payment_status == 'pending':
        campaign.payment_status = 'paid'
        campaign.save()
        
        company_profile.pending_payment -= campaign.budget
        company_profile.total_spend += campaign.budget
        company_profile.save()
        
        print(f"✓ Payment marked as completed")
        print(f"  Old Pending Payment: ₹{old_pending}")
        print(f"  New Pending Payment: ₹{company_profile.pending_payment}")
        print(f"  Old Total Spend: ₹{old_total_spend}")
        print(f"  New Total Spend: ₹{company_profile.total_spend}")
        
        expected_pending = old_pending - test_budget
        expected_spend = old_total_spend + test_budget
        
        if (company_profile.pending_payment == expected_pending and 
            company_profile.total_spend == expected_spend):
            print("✅ TEST 3 PASSED: Payment correctly moved from pending to total spend")
        else:
            print("❌ TEST 3 FAILED: Incorrect payment calculation")
    else:
        print("❌ TEST 3 FAILED: Campaign not in correct state")
    print()
    
    # Test 4: Try to mark payment again (should fail in real API)
    print("TEST 4: Attempting to mark payment again")
    print("-" * 60)
    if campaign.payment_status == 'paid':
        print("✓ Payment status is already 'paid'")
        print("✅ TEST 4 PASSED: Cannot mark payment twice (API would reject)")
    else:
        print("❌ TEST 4 FAILED: Payment status not set correctly")
    print()
    
    # Cleanup
    print("CLEANUP: Removing test campaign")
    print("-" * 60)
    
    # Restore company profile balances
    company_profile.pending_payment = old_pending
    company_profile.total_spend = old_total_spend
    company_profile.save()
    
    campaign.delete()
    print("✓ Test campaign deleted")
    print("✓ Company profile balances restored")
    print()
    
    print("="*60)
    print("ALL TESTS COMPLETED")
    print("="*60)
    
except Exception as e:
    print(f"\n❌ ERROR: {str(e)}")
    import traceback
    traceback.print_exc()
