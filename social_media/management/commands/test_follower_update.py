from django.core.management.base import BaseCommand
from accounts.models import InfluencerProfile
from social_media.services import SocialMediaService
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Test follower update functionality'

    def add_arguments(self, parser):
        parser.add_argument(
            '--username',
            type=str,
            help='Username of the influencer to test',
        )
        parser.add_argument(
            '--platform',
            type=str,
            choices=['instagram', 'youtube'],
            help='Platform to test (instagram or youtube)',
        )

    def handle(self, *args, **options):
        username = options.get('username')
        platform = options.get('platform')

        if username:
            try:
                profile = InfluencerProfile.objects.get(user__username=username)
                self.stdout.write(f"Testing follower update for {username}...")
                
                if platform:
                    # Test specific platform
                    if platform == 'instagram' and profile.instagram_handle:
                        followers = SocialMediaService.get_instagram_followers(profile.instagram_handle)
                        self.stdout.write(f"Instagram followers for @{profile.instagram_handle}: {followers}")
                    elif platform == 'youtube' and profile.youtube_channel:
                        subscribers = SocialMediaService.get_youtube_subscribers(profile.youtube_channel)
                        self.stdout.write(f"YouTube subscribers for {profile.youtube_channel}: {subscribers}")
                    else:
                        self.stdout.write(f"No {platform} handle found for {username}")
                else:
                    # Test all platforms
                    results = SocialMediaService.update_follower_counts(profile)
                    self.stdout.write(f"Update results: {results}")
                    
                    # Refresh profile
                    profile.refresh_from_db()
                    self.stdout.write(f"Updated follower count: {profile.followers_count}")
                    
            except InfluencerProfile.DoesNotExist:
                self.stdout.write(f"Influencer profile not found for username: {username}")
        else:
            # Test with sample data
            self.stdout.write("Testing Instagram API with sample username...")
            followers = SocialMediaService.get_instagram_followers('instagram')  # Official Instagram account
            self.stdout.write(f"Instagram official account followers: {followers}")
            
            self.stdout.write("\nTesting YouTube API with sample channel...")
            subscribers = SocialMediaService.get_youtube_subscribers('UC_x5XG1OV2P6uZZ5FSM9Ttw')  # Google Developers
            self.stdout.write(f"Google Developers YouTube subscribers: {subscribers}")
            
            self.stdout.write("\nTo test with a specific user, use: --username <username>")
            self.stdout.write("To test a specific platform, add: --platform instagram|youtube")