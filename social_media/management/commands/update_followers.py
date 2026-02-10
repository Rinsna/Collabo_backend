from django.core.management.base import BaseCommand
from social_media.tasks import update_all_influencer_followers, schedule_follower_updates

class Command(BaseCommand):
    help = 'Update follower counts for all influencers'

    def add_arguments(self, parser):
        parser.add_argument(
            '--async',
            action='store_true',
            help='Run updates asynchronously using Celery',
        )
        parser.add_argument(
            '--schedule',
            action='store_true',
            help='Schedule updates for profiles that need updating',
        )

    def handle(self, *args, **options):
        if options['schedule']:
            self.stdout.write('Scheduling follower updates...')
            result = schedule_follower_updates.delay()
            self.stdout.write(
                self.style.SUCCESS(f'Scheduled updates. Task ID: {result.id}')
            )
        elif options['async']:
            self.stdout.write('Starting async follower updates...')
            result = update_all_influencer_followers.delay()
            self.stdout.write(
                self.style.SUCCESS(f'Started async update. Task ID: {result.id}')
            )
        else:
            self.stdout.write('Starting synchronous follower updates...')
            result = update_all_influencer_followers()
            
            success_count = sum(1 for r in result if 'error' not in r)
            error_count = len(result) - success_count
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'Update completed. Success: {success_count}, Errors: {error_count}'
                )
            )
            
            if error_count > 0:
                self.stdout.write(self.style.WARNING('Errors occurred:'))
                for r in result:
                    if 'error' in r:
                        self.stdout.write(f"  Profile {r.get('profile_id', 'unknown')}: {r['error']}")