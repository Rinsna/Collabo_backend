#!/usr/bin/env python
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'influencer_platform.settings')
django.setup()

from collaborations.models import Campaign

print("=== Campaign Budget Debug ===")
campaigns = Campaign.objects.all()

if campaigns.exists():
    print(f"Found {campaigns.count()} campaigns:")
    for campaign in campaigns:
        print(f"- {campaign.title}: Budget = {campaign.budget} (type: {type(campaign.budget)})")
        print(f"  Raw value: {repr(campaign.budget)}")
        print(f"  Float value: {float(campaign.budget)}")
        print(f"  Formatted: {campaign.budget:,.2f}")
        print()
    
    total_budget = sum(float(c.budget) for c in campaigns)
    print(f"Total Budget: {total_budget}")
    print(f"Total Budget Formatted: {total_budget:,.2f}")
else:
    print("No campaigns found in database")