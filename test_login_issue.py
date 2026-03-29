#!/usr/bin/env python3
"""
Test login to identify the 400 error
"""
import requests
import json

def test_login():
    print("=" * 80)
    print("🔐 TESTING LOGIN ISSUE")
    print("=" * 80)
    
    # Test different login attempts
    test_cases = [
        {
            'name': 'Company Login (test@test.com)',
            'data': {'email': 'company@test.com', 'password': 'test123'}
        },
        {
            'name': 'Influencer Login (test@test.com)',
            'data': {'email': 'test@test.com', 'password': 'test123'}
        },
        {
            'name': 'Admin Login',
            'data': {'email': 'rinsnac44@gmail.com', 'password': 'test123'}
        }
    ]
    
    for test in test_cases:
        print(f"\n📝 Test: {test['name']}")
        print(f"Data: {json.dumps(test['data'], indent=2)}")
        
        try:
            response = requests.post(
                'http://localhost:8000/api/auth/login/',
                json=test['data'],
                headers={'Content-Type': 'application/json'}
            )
            
            print(f"Status Code: {response.status_code}")
            
            if response.status_code == 200:
                print("✅ Login successful!")
                data = response.json()
                print(f"User: {data.get('user', {}).get('username')}")
                print(f"Token: {data.get('access', '')[:20]}...")
            else:
                print(f"❌ Login failed!")
                print(f"Response: {response.text}")
                
        except Exception as e:
            print(f"❌ Error: {str(e)}")

if __name__ == '__main__':
    test_login()
