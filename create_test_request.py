#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'influencer_platform.settings')
django.setup()

from collaborations.models import CollaborationRequest, Campaign
from accounts.models import User

# Get users and campaign
influencer = User.objects.filter(user_type='influencer').first()
company = User.objects.filter(user_type='company').first()
campaign = Campaign.objects.first()

if influencer and company and campaign:
    # Create a new collaboration request
    request = CollaborationRequest.objects.create(
        campaign=campaign,
        influencer=influencer,
        company=company,
        message="Test request for acceptance",
        proposed_rate=750.00,
        status='pending'
    )
    
    print(f"Created new collaboration request:")
    print(f"ID: {request.id}")
    print(f"Campaign: {request.campaign.title}")
    print(f"Influencer: {request.influencer.username}")
    print(f"Company: {request.company.username}")
    print(f"Status: {request.status}")
else:
    print("Missing required data (influencer, company, or campaign)")