"""
Django management command to sync social media accounts
"""

from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth import get_user_model
from social_media.sync_service import sync_service
from social_media.models import SocialMediaAccount

User = get_user_model()


class Command(BaseCommand):
    help = 'Sync social media accounts'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--all',
            action='store_true',
            help='Sync all active social media accounts'
        )
        
        parser.add_argument(
            '--user',
            type=int,
            help='Sync accounts for a specific user ID'
        )
        
        parser.add_argument(
            '--platform',
            type=str,
            choices=['instagram', 'youtube', 'tiktok', 'twitter', 'facebook'],
            help='Sync accounts for a specific platform'
        )
        
        parser.add_argument(
            '--account',
            type=int,
            help='Sync a specific account ID'
        )
        
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be synced without actually syncing'
        )
    
    def handle(self, *args, **options):
        if options['dry_run']:
            self.stdout.write(
                self.style.WARNING('DRY RUN MODE - No actual syncing will be performed')
            )
        
        try:
            if options['all']:
                self.sync_all_accounts(options['dry_run'])
            elif options['user']:
                self.sync_user_accounts(options['user'], options['dry_run'])
            elif options['platform']:
                self.sync_platform_accounts(options['platform'], options['dry_run'])
            elif options['account']:
                self.sync_single_account(options['account'], options['dry_run'])
            else:
                raise CommandError('Please specify --all, --user, --platform, or --account')
        
        except Exception as e:
            raise CommandError(f'Sync failed: {e}')
    
    def sync_all_accounts(self, dry_run=False):
        """Sync all active accounts"""
        accounts = SocialMediaAccount.objects.filter(status='active')
        
        self.stdout.write(f'Found {accounts.count()} active accounts to sync')
        
        if dry_run:
            for account in accounts:
                self.stdout.write(f'  Would sync: {account}')
            return
        
        job_id = sync_service.sync_all_accounts()
        self.stdout.write(
            self.style.SUCCESS(f'Started sync job: {job_id}')
        )
    
    def sync_user_accounts(self, user_id, dry_run=False):
        """Sync accounts for a specific user"""
        try:
            user = User.objects.get(id=user_id)
            accounts = user.social_accounts.filter(status='active')
            
            self.stdout.write(f'Found {accounts.count()} active accounts for user {user.username}')
            
            if dry_run:
                for account in accounts:
                    self.stdout.write(f'  Would sync: {account}')
                return
            
            job_id = sync_service.sync_user_accounts(user_id)
            self.stdout.write(
                self.style.SUCCESS(f'Started user sync job: {job_id}')
            )
        
        except User.DoesNotExist:
            raise CommandError(f'User with ID {user_id} not found')
    
    def sync_platform_accounts(self, platform, dry_run=False):
        """Sync accounts for a specific platform"""
        accounts = SocialMediaAccount.objects.filter(
            platform=platform,
            status='active'
        )
        
        self.stdout.write(f'Found {accounts.count()} active {platform} accounts to sync')
        
        if dry_run:
            for account in accounts:
                self.stdout.write(f'  Would sync: {account}')
            return
        
        successful = 0
        failed = 0
        
        for account in accounts:
            try:
                success = sync_service.sync_single_account_by_id(account.id)
                if success:
                    successful += 1
                    self.stdout.write(f'  ✓ Synced: {account}')
                else:
                    failed += 1
                    self.stdout.write(f'  ✗ Failed: {account}')
            except Exception as e:
                failed += 1
                self.stdout.write(f'  ✗ Error syncing {account}: {e}')
        
        self.stdout.write(
            self.style.SUCCESS(f'Platform sync completed: {successful} successful, {failed} failed')
        )
    
    def sync_single_account(self, account_id, dry_run=False):
        """Sync a single account"""
        try:
            account = SocialMediaAccount.objects.get(id=account_id)
            
            self.stdout.write(f'Account to sync: {account}')
            
            if dry_run:
                self.stdout.write('  Would sync this account')
                return
            
            success = sync_service.sync_single_account_by_id(account_id)
            
            if success:
                self.stdout.write(
                    self.style.SUCCESS(f'Successfully synced account: {account}')
                )
            else:
                self.stdout.write(
                    self.style.ERROR(f'Failed to sync account: {account}')
                )
        
        except SocialMediaAccount.DoesNotExist:
            raise CommandError(f'Account with ID {account_id} not found')