#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'influencer_platform.settings')
django.setup()

from accounts.models import User, CompanyProfile

print("Company users and their profiles:")
companies = User.objects.filter(user_type='company')
for company in companies:
    try:
        profile = company.company_profile
        print(f"{company.username}: Has profile - {profile.company_name}")
    except CompanyProfile.DoesNotExist:
        print(f"{company.username}: No profile")

print("\nAll campaigns:")
from collaborations.models import Campaign
campaigns = Campaign.objects.all()
for campaign in campaigns:
    print(f"Campaign: {campaign.title} by {campaign.company.username}")