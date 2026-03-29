"""
Django management command to clean up old social media data
"""

from django.core.management.base import BaseCommand
from social_media.sync_service import sync_service


class Command(BaseCommand):
    help = 'Clean up old social media sync data'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--days',
            type=int,
            default=90,
            help='Delete data older than this many days (default: 90)'
        )
        
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be deleted without actually deleting'
        )
    
    def handle(self, *args, **options):
        days = options['days']
        dry_run = options['dry_run']
        
        if dry_run:
            self.stdout.write(
                self.style.WARNING('DRY RUN MODE - No actual deletion will be performed')
            )
        
        self.stdout.write(f'Cleaning up data older than {days} days...')
        
        if not dry_run:
            result = sync_service.cleanup_old_data(days=days)
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'Cleanup completed:\n'
                    f'  - Deleted {result["deleted_history_records"]} follower history records\n'
                    f'  - Deleted {result["deleted_sync_jobs"]} sync jobs'
                )
            )
        else:
            # For dry run, we'd need to implement a preview method
            self.stdout.write('Would clean up old follower history and sync job records')