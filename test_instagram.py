import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'influencer_platform.settings')
django.setup()

from accounts.youtube_service import InstagramService, VideoStatsService

# Test Instagram
url = 'https://www.instagram.com/reel/DT-HQ39Dw0w/'
print(f"Testing Instagram URL: {url}")
stats = InstagramService.get_post_stats(url)
print(f"Result: {stats}")

# Test with VideoStatsService
print("\nTesting with VideoStatsService:")
stats2 = VideoStatsService.get_stats(url)
print(f"Result: {stats2}")
