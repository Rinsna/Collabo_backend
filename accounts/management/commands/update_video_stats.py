from django.core.management.base import BaseCommand
from accounts.models import InfluencerProfile
from accounts.youtube_service import VideoStatsService

class Command(BaseCommand):
    help = 'Update video statistics (YouTube & Instagram) for all influencer profiles'

    def add_arguments(self, parser):
        parser.add_argument(
            '--profile-id',
            type=int,
            help='Update stats for a specific profile ID',
        )

    def handle(self, *args, **options):
        profile_id = options.get('profile_id')
        
        if profile_id:
            # Update specific profile
            try:
                profile = InfluencerProfile.objects.get(id=profile_id)
                self.stdout.write(f'Updating stats for {profile.user.username}...')
                
                if VideoStatsService.update_profile_video_stats(profile):
                    self.stdout.write(self.style.SUCCESS(f'✓ Updated {profile.user.username}'))
                    self.stdout.write(f'  Latest Review - Views: {profile.latest_product_review_views}, Likes: {profile.latest_product_review_likes}')
                    self.stdout.write(f'  Most Viewed - Views: {profile.most_viewed_content_views}, Likes: {profile.most_viewed_content_likes}')
                else:
                    self.stdout.write(self.style.WARNING(f'⚠ No videos to update for {profile.user.username}'))
                    
            except InfluencerProfile.DoesNotExist:
                self.stdout.write(self.style.ERROR(f'Profile with ID {profile_id} not found'))
        else:
            # Update all profiles
            profiles = InfluencerProfile.objects.filter(
                latest_product_review_link__isnull=False
            ) | InfluencerProfile.objects.filter(
                most_viewed_content_link__isnull=False
            )
            
            # Exclude empty strings
            profiles = profiles.exclude(latest_product_review_link='').exclude(most_viewed_content_link='')
            
            total = profiles.count()
            updated = 0
            
            self.stdout.write(f'Found {total} profiles with video links')
            
            for profile in profiles:
                self.stdout.write(f'\nUpdating {profile.user.username}...')
                
                if VideoStatsService.update_profile_video_stats(profile):
                    updated += 1
                    self.stdout.write(self.style.SUCCESS(f'  ✓ Updated'))
                    self.stdout.write(f'  Latest Review - Views: {profile.latest_product_review_views}, Likes: {profile.latest_product_review_likes}')
                    self.stdout.write(f'  Most Viewed - Views: {profile.most_viewed_content_views}, Likes: {profile.most_viewed_content_likes}')
                else:
                    self.stdout.write(self.style.WARNING(f'  ⚠ Failed to fetch stats'))
            
            self.stdout.write(self.style.SUCCESS(f'\nCompleted! Updated {updated}/{total} profiles'))
