#!/usr/bin/env python3
"""
Test send message functionality to identify issues
"""
import os
import sys
import django
import requests
import json

# Add the backend directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'influencer_platform.settings')
django.setup()

from accounts.models import User
from collaborations.models import DirectCollaborationRequest

def test_send_message():
    print("=" * 80)
    print("🧪 TESTING SEND MESSAGE FUNCTIONALITY")
    print("=" * 80)
    
    # Get test users
    company_user = User.objects.filter(email='company@test.com').first()
    influencer_user = User.objects.filter(email='test@test.com').first()
    
    if not company_user or not influencer_user:
        print("❌ Missing test users. Need at least 1 company and 1 influencer.")
        return
    
    print(f"✅ Company User: {company_user.username} (ID: {company_user.id})")
    print(f"✅ Influencer User: {influencer_user.username} (ID: {influencer_user.id})")
    
    # Test 1: Login as company
    print(f"\n📝 Test 1: Company Login")
    login_response = requests.post('http://localhost:8000/api/auth/login/', {
        'email': 'company@test.com',
        'password': 'test123'
    })
    
    if login_response.status_code != 200:
        print(f"❌ Company login failed: {login_response.status_code}")
        print(f"Response: {login_response.text}")
        return
    
    company_token = login_response.json()['access']
    print(f"✅ Company login successful")
    
    # Test 2: Send Direct Message
    print(f"\n📝 Test 2: Send Direct Message")
    headers = {'Authorization': f'Bearer {company_token}'}
    message_data = {
        'influencer': influencer_user.id,
        'message': 'Hi! I would like to collaborate with you on a fashion campaign.',
        'campaign_details': {
            'title': 'Fashion Campaign Test',
            'type': 'message',
            'description': 'Test direct message'
        }
    }
    
    print(f"Sending message data: {json.dumps(message_data, indent=2)}")
    
    message_response = requests.post(
        'http://localhost:8000/api/collaborations/direct-requests/',
        json=message_data,
        headers=headers
    )
    
    print(f"Response Status: {message_response.status_code}")
    print(f"Response Data: {json.dumps(message_response.json(), indent=2)}")
    
    if message_response.status_code == 201:
        print("✅ Direct message sent successfully!")
        message_id = message_response.json()['id']
    else:
        print("❌ Direct message failed!")
        return
    
    # Test 3: Send Collaboration Request
    print(f"\n📝 Test 3: Send Collaboration Request")
    collaboration_data = {
        'influencer': influencer_user.id,
        'message': 'I have a detailed campaign proposal for you.',
        'proposed_rate': 5000.00,
        'campaign_details': {
            'title': 'Summer Fashion Collection 2024',
            'description': 'Promote our new summer collection with 3 Instagram posts',
            'timeline': '2 weeks',
            'deliverables': '3 Instagram posts, 2 stories, 1 reel',
            'requirements': 'Use hashtag #SummerVibes2024, tag @ourbrand'
        }
    }
    
    print(f"Sending collaboration data: {json.dumps(collaboration_data, indent=2)}")
    
    collab_response = requests.post(
        'http://localhost:8000/api/collaborations/direct-requests/',
        json=collaboration_data,
        headers=headers
    )
    
    print(f"Response Status: {collab_response.status_code}")
    print(f"Response Data: {json.dumps(collab_response.json(), indent=2)}")
    
    if collab_response.status_code == 201:
        print("✅ Collaboration request sent successfully!")
    else:
        print("❌ Collaboration request failed!")
    
    # Test 4: Check database records
    print(f"\n📝 Test 4: Database Verification")
    direct_requests = DirectCollaborationRequest.objects.filter(
        company=company_user,
        influencer=influencer_user
    ).order_by('-created_at')
    
    print(f"Total direct requests in database: {direct_requests.count()}")
    for req in direct_requests[:3]:  # Show last 3
        print(f"  - ID: {req.id}, Message: {req.message[:50]}..., Status: {req.status}")
        print(f"    Campaign Details: {req.campaign_details}")
    
    # Test 5: Login as influencer and check received messages
    print(f"\n📝 Test 5: Influencer Login & Check Messages")
    influencer_login = requests.post('http://localhost:8000/api/auth/login/', {
        'email': 'test@test.com',
        'password': 'test123'
    })
    
    if influencer_login.status_code == 200:
        influencer_token = influencer_login.json()['access']
        print(f"✅ Influencer login successful")
        
        # Check received direct requests
        influencer_headers = {'Authorization': f'Bearer {influencer_token}'}
        received_response = requests.get(
            'http://localhost:8000/api/collaborations/direct-requests/',
            headers=influencer_headers
        )
        
        print(f"Received messages status: {received_response.status_code}")
        if received_response.status_code == 200:
            received_data = received_response.json()
            print(f"Messages received by influencer: {len(received_data.get('results', []))}")
            for msg in received_data.get('results', [])[:2]:
                print(f"  - From: {msg.get('company_name', 'Unknown')}")
                print(f"    Message: {msg['message'][:50]}...")
                print(f"    Status: {msg['status']}")
        else:
            print(f"❌ Failed to get received messages: {received_response.text}")
    else:
        print(f"❌ Influencer login failed: {influencer_login.status_code}")
    
    print(f"\n" + "=" * 80)
    print("🏁 Test completed!")
    print("=" * 80)

if __name__ == '__main__':
    test_send_message()