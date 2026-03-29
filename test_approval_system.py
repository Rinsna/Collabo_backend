#!/usr/bin/env python
"""
Test script for influencer approval system
Run: python test_approval_system.py
"""

import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'influencer_platform.settings')
django.setup()

from accounts.models import User
from django.contrib.auth import authenticate

def test_approval_system():
    print("=" * 60)
    print("INFLUENCER APPROVAL SYSTEM TEST")
    print("=" * 60)
    
    # Test 1: Create a new influencer
    print("\n1. Creating new influencer...")
    try:
        influencer = User.objects.create_user(
            username='test_influencer',
            email='test_influencer@example.com',
            password='TestPass123',
            user_type='influencer'
        )
        print(f"✓ Influencer created: {influencer.username}")
        print(f"  - is_approved: {influencer.is_approved}")
        print(f"  - approval_status: {influencer.approval_status}")
        assert influencer.is_approved == False, "New influencer should not be approved"
        assert influencer.approval_status == 'pending', "New influencer should be pending"
        print("✓ Status correctly set to pending")
    except Exception as e:
        print(f"✗ Error: {e}")
    
    # Test 2: Create a new company
    print("\n2. Creating new company...")
    try:
        company = User.objects.create_user(
            username='test_company',
            email='test_company@example.com',
            password='TestPass123',
            user_type='company'
        )
        print(f"✓ Company created: {company.username}")
        print(f"  - is_approved: {company.is_approved}")
        print(f"  - approval_status: {company.approval_status}")
        assert company.is_approved == True, "New company should be auto-approved"
        assert company.approval_status == 'approved', "New company should be approved"
        print("✓ Status correctly set to approved")
    except Exception as e:
        print(f"✗ Error: {e}")
    
    # Test 3: Try to authenticate pending influencer
    print("\n3. Testing pending influencer authentication...")
    try:
        user = authenticate(username='test_influencer@example.com', password='TestPass123')
        if user:
            print(f"✓ Authentication successful for: {user.username}")
            print(f"  - But login should be blocked by serializer validation")
        else:
            print("✗ Authentication failed")
    except Exception as e:
        print(f"✗ Error: {e}")
    
    # Test 4: Approve influencer
    print("\n4. Approving influencer...")
    try:
        influencer.is_approved = True
        influencer.approval_status = 'approved'
        influencer.save()
        print(f"✓ Influencer approved: {influencer.username}")
        print(f"  - is_approved: {influencer.is_approved}")
        print(f"  - approval_status: {influencer.approval_status}")
    except Exception as e:
        print(f"✗ Error: {e}")
    
    # Test 5: Try to authenticate approved influencer
    print("\n5. Testing approved influencer authentication...")
    try:
        user = authenticate(username='test_influencer@example.com', password='TestPass123')
        if user:
            print(f"✓ Authentication successful for: {user.username}")
            print(f"  - Can now login and get JWT token")
        else:
            print("✗ Authentication failed")
    except Exception as e:
        print(f"✗ Error: {e}")
    
    # Test 6: Reject influencer
    print("\n6. Rejecting influencer...")
    try:
        influencer.is_approved = False
        influencer.approval_status = 'rejected'
        influencer.rejection_reason = 'Test rejection'
        influencer.save()
        print(f"✓ Influencer rejected: {influencer.username}")
        print(f"  - is_approved: {influencer.is_approved}")
        print(f"  - approval_status: {influencer.approval_status}")
        print(f"  - rejection_reason: {influencer.rejection_reason}")
    except Exception as e:
        print(f"✗ Error: {e}")
    
    # Test 7: Count statistics
    print("\n7. Approval statistics...")
    try:
        total = User.objects.filter(user_type='influencer').count()
        pending = User.objects.filter(user_type='influencer', approval_status='pending').count()
        approved = User.objects.filter(user_type='influencer', approval_status='approved').count()
        rejected = User.objects.filter(user_type='influencer', approval_status='rejected').count()
        
        print(f"✓ Statistics:")
        print(f"  - Total influencers: {total}")
        print(f"  - Pending: {pending}")
        print(f"  - Approved: {approved}")
        print(f"  - Rejected: {rejected}")
    except Exception as e:
        print(f"✗ Error: {e}")
    
    # Cleanup
    print("\n8. Cleaning up test data...")
    try:
        User.objects.filter(username__in=['test_influencer', 'test_company']).delete()
        print("✓ Test data cleaned up")
    except Exception as e:
        print(f"✗ Error: {e}")
    
    print("\n" + "=" * 60)
    print("TEST COMPLETE")
    print("=" * 60)

if __name__ == '__main__':
    test_approval_system()
