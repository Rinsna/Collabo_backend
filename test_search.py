#!/usr/bin/env python
import os
import django
import sys

# Add the project directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'influencer_platform.settings')
django.setup()

from accounts.models import InfluencerProfile, User
from accounts.serializers import InfluencerProfileSerializer
from rest_framework.test import APIRequestFactory
from rest_framework.request import Request
from accounts.views import InfluencerListView

def test_search():
    print("Testing influencer search functionality...")
    
    # Create a test request
    factory = APIRequestFactory()
    
    # Test 1: Get all influencers
    print("\n1. Testing: Get all influencers")
    request = factory.get('/api/auth/influencers/')
    view = InfluencerListView()
    view.request = Request(request)
    queryset = view.get_queryset()
    print(f"Total influencers: {queryset.count()}")
    
    # Test 2: Search by username
    print("\n2. Testing: Search functionality")
    request = factory.get('/api/auth/influencers/?search=test')
    view = InfluencerListView()
    view.request = Request(request)
    view.filter_queryset = lambda qs: view.filter_backends[0]().filter_queryset(view.request, qs, view)
    
    # Get all influencers and their usernames
    all_influencers = InfluencerProfile.objects.all()
    print("Available influencers:")
    for inf in all_influencers:
        print(f"  - {inf.user.username} (category: {inf.category}, bio: {inf.bio[:50] if inf.bio else 'No bio'})")
    
    # Test 3: Category filter
    print("\n3. Testing: Category filter")
    request = factory.get('/api/auth/influencers/?category=fashion')
    view = InfluencerListView()
    view.request = Request(request)
    filtered_queryset = view.get_queryset()
    print(f"Fashion influencers: {filtered_queryset.count()}")
    
    # Test 4: Ordering
    print("\n4. Testing: Ordering by followers")
    request = factory.get('/api/auth/influencers/?ordering=-followers_count')
    view = InfluencerListView()
    view.request = Request(request)
    ordered_queryset = view.get_queryset().order_by('-followers_count')
    print("Top 3 influencers by followers:")
    for inf in ordered_queryset[:3]:
        print(f"  - {inf.user.username}: {inf.followers_count} followers")

if __name__ == '__main__':
    test_search()