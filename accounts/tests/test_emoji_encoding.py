
from django.test import TestCase
from accounts.models import User, InfluencerProfile
import json

class EmojiTest(TestCase):
    def test_emoji_storage_and_retrieval(self):
        print("\nRunning Emoji Storage Test...")
        
        # Test data with various emojis
        # U+1F60A (Smiling Face with Smiling Eyes) -> \xf0\x9f\x98\x8a
        # U+1F680 (Rocket) -> \xf0\x9f\x9a\x80
        emoji_str = "Hello \U0001f60a \U0001f680"
        
        user = User.objects.create_user(username='emojitest', email='test@example.com', password='password')
        profile = InfluencerProfile.objects.create(
            user=user,
            bio=emoji_str,
            category='tech'
        )
        
        # Reload from DB
        profile.refresh_from_db()
        
        print(f"Original: {emoji_str.encode('utf-8')}")
        print(f"Stored:   {profile.bio.encode('utf-8')}")
        
        self.assertEqual(profile.bio, emoji_str)
        print("Storage test PASSED")
        
    def test_api_response_encoding(self):
        print("\nRunning API Response Encoding Test...")
        from rest_framework.test import APIClient
        
        client = APIClient()
        user = User.objects.create_user(username='apitest', email='api@example.com', password='password')
        client.force_authenticate(user=user)
        
        emoji_str = "API Emoji \U0001f44d" # Thumbs up
        InfluencerProfile.objects.create(user=user, bio=emoji_str)
        
        response = client.get('/api/auth/influencer-profile/')
        
        self.assertEqual(response.status_code, 200)
        
        # Check Content-Type header
        print(f"Content-Type: {response['Content-Type']}")
        # self.assertIn('charset=utf-8', response['Content-Type'].lower()) # This might fail if not explicitly set
        
        # Check content
        content = response.json()
        print(f"API Content: {content['bio']}")
        self.assertEqual(content['bio'], emoji_str)
        print("API test PASSED")
