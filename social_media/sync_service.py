"""
Social Media Sync Service
Handles automatic follower count updates and social media data synchronization
"""

import uuid
import logging
from typing import List, Dict, Optional
from datetime import datetime, timedelta
from django.utils import timezone
from django.db import transaction
from django.contrib.auth import get_user_model
from django.core.cache import cache

from .models import SocialMediaAccount, FollowerHistory, SyncJob
from .api_clients import get_api_client, APIError, UnauthorizedError, RateLimitError
from accounts.models import InfluencerProfile

User = get_user_model()
logger = logging.getLogger(__name__)


class SocialMediaSyncService:
    """Service class for synchronizing social media data"""
    
    def __init__(self):
        self.rate_limit_cache_prefix = "social_sync_rate_limit"
        self.max_retries = 3
        self.retry_delay = 300  # 5 minutes
    
    def sync_all_accounts(self) -> str:
        """Sync all active social media accounts"""
        job_id = str(uuid.uuid4())
        
        try:
            # Create sync job
            sync_job = SyncJob.objects.create(
                job_id=job_id,
                job_type='full_sync',
                status='pending'
            )
            
            # Get all active accounts
            accounts = SocialMediaAccount.objects.filter(
                status='active'
            ).select_related('user')
            
            sync_job.mark_started()
            
            successful_syncs = 0
            failed_syncs = 0
            error_details = {}
            
            for account in accounts:
                try:
                    # Check rate limits
                    if self._is_rate_limited(account.platform):
                        logger.warning(f"Rate limited for {account.platform}, skipping {account}")
                        continue
                    
                    # Sync individual account
                    success = self._sync_single_account(account)
                    
                    if success:
                        successful_syncs += 1
                        account.reset_error_count()
                    else:
                        failed_syncs += 1
                
                except Exception as e:
                    logger.error(f"Failed to sync account {account}: {e}")
                    account.mark_error(str(e))
                    failed_syncs += 1
                    error_details[str(account.id)] = str(e)
            
            # Update job results
            sync_job.accounts_processed = len(accounts)
            sync_job.accounts_successful = successful_syncs
            sync_job.accounts_failed = failed_syncs
            sync_job.error_details = error_details
            sync_job.mark_completed()
            
            logger.info(f"Sync job {job_id} completed: {successful_syncs} successful, {failed_syncs} failed")
            
            return job_id
        
        except Exception as e:
            logger.error(f"Sync job {job_id} failed: {e}")
            if 'sync_job' in locals():
                sync_job.mark_failed({'error': str(e)})
            raise
    
    def sync_user_accounts(self, user_id: int) -> str:
        """Sync all accounts for a specific user"""
        job_id = str(uuid.uuid4())
        
        try:
            user = User.objects.get(id=user_id)
            
            sync_job = SyncJob.objects.create(
                job_id=job_id,
                job_type='user_sync',
                user=user,
                status='pending'
            )
            
            accounts = user.social_accounts.filter(status='active')
            sync_job.mark_started()
            
            successful_syncs = 0
            failed_syncs = 0
            error_details = {}
            
            for account in accounts:
                try:
                    if self._is_rate_limited(account.platform):
                        continue
                    
                    success = self._sync_single_account(account)
                    
                    if success:
                        successful_syncs += 1
                        account.reset_error_count()
                    else:
                        failed_syncs += 1
                
                except Exception as e:
                    logger.error(f"Failed to sync account {account}: {e}")
                    account.mark_error(str(e))
                    failed_syncs += 1
                    error_details[str(account.id)] = str(e)
            
            sync_job.accounts_processed = len(accounts)
            sync_job.accounts_successful = successful_syncs
            sync_job.accounts_failed = failed_syncs
            sync_job.error_details = error_details
            sync_job.mark_completed()
            
            # Update user's influencer profile if exists
            if hasattr(user, 'influencer_profile'):
                self._update_influencer_profile(user.influencer_profile)
            
            return job_id
        
        except User.DoesNotExist:
            logger.error(f"User {user_id} not found")
            raise ValueError(f"User {user_id} not found")
        except Exception as e:
            logger.error(f"User sync job {job_id} failed: {e}")
            if 'sync_job' in locals():
                sync_job.mark_failed({'error': str(e)})
            raise
    
    def sync_single_account_by_id(self, account_id: int) -> bool:
        """Sync a single social media account by ID"""
        try:
            account = SocialMediaAccount.objects.get(id=account_id)
            return self._sync_single_account(account)
        except SocialMediaAccount.DoesNotExist:
            logger.error(f"Social media account {account_id} not found")
            return False
    
    def _sync_single_account(self, account: SocialMediaAccount) -> bool:
        """Sync a single social media account"""
        try:
            logger.info(f"Syncing account: {account}")
            
            # Check if token is expired and try to refresh
            if account.is_token_expired():
                logger.info(f"Token expired for {account}, attempting refresh")
                if not self._refresh_account_token(account):
                    logger.error(f"Failed to refresh token for {account}")
                    return False
            
            # Get API client
            client = get_api_client(
                account.platform,
                account.get_access_token(),
                account.get_refresh_token()
            )
            
            # Fetch engagement metrics
            metrics = client.get_engagement_metrics()
            
            # Create follower history record
            with transaction.atomic():
                follower_history = FollowerHistory.objects.create(
                    social_account=account,
                    follower_count=metrics['follower_count'],
                    following_count=metrics.get('following_count', 0),
                    posts_count=metrics.get('posts_count', 0),
                    engagement_rate=metrics.get('engagement_rate', 0),
                    likes_count=metrics.get('likes_count', 0),
                    comments_count=metrics.get('comments_count', 0),
                    shares_count=metrics.get('shares_count', 0),
                    views_count=metrics.get('views_count', 0),
                    sync_source='api'
                )
                
                # Update account last sync time
                account.last_sync = timezone.now()
                account.save()
                
                logger.info(f"Successfully synced {account}: {metrics['follower_count']} followers")
            
            return True
        
        except UnauthorizedError as e:
            logger.error(f"Unauthorized error for {account}: {e}")
            account.status = 'expired'
            account.mark_error(str(e))
            return False
        
        except RateLimitError as e:
            logger.warning(f"Rate limit hit for {account}: {e}")
            self._set_rate_limit(account.platform)
            account.mark_error(str(e))
            return False
        
        except APIError as e:
            logger.error(f"API error for {account}: {e}")
            account.mark_error(str(e))
            return False
        
        except Exception as e:
            logger.error(f"Unexpected error syncing {account}: {e}")
            account.mark_error(str(e))
            return False
    
    def _refresh_account_token(self, account: SocialMediaAccount) -> bool:
        """Refresh access token for an account"""
        try:
            if not account.get_refresh_token():
                logger.error(f"No refresh token available for {account}")
                return False
            
            client = get_api_client(
                account.platform,
                account.get_access_token(),
                account.get_refresh_token()
            )
            
            new_access_token, new_refresh_token, expires_at = client.refresh_access_token()
            
            # Update account with new tokens
            account.set_access_token(new_access_token)
            if new_refresh_token:
                account.set_refresh_token(new_refresh_token)
            account.token_expires_at = expires_at
            account.status = 'active'
            account.save()
            
            logger.info(f"Successfully refreshed token for {account}")
            return True
        
        except Exception as e:
            logger.error(f"Failed to refresh token for {account}: {e}")
            account.status = 'expired'
            account.save()
            return False
    
    def _update_influencer_profile(self, profile: InfluencerProfile):
        """Update influencer profile with latest social media data"""
        try:
            # Get all social accounts for this user
            accounts = profile.user.social_accounts.filter(status='active')
            
            total_followers = 0
            total_engagement = 0
            account_count = 0
            
            for account in accounts:
                # Get latest follower history
                latest_history = account.follower_history.first()
                if latest_history:
                    total_followers += latest_history.follower_count
                    total_engagement += float(latest_history.engagement_rate)
                    account_count += 1
            
            # Update profile
            if account_count > 0:
                profile.followers_count = total_followers
                profile.engagement_rate = total_engagement / account_count
                profile.save()
                
                logger.info(f"Updated influencer profile for {profile.user}: {total_followers} followers")
        
        except Exception as e:
            logger.error(f"Failed to update influencer profile {profile}: {e}")
    
    def _is_rate_limited(self, platform: str) -> bool:
        """Check if platform is currently rate limited"""
        cache_key = f"{self.rate_limit_cache_prefix}:{platform}"
        return cache.get(cache_key, False)
    
    def _set_rate_limit(self, platform: str, duration: int = 3600):
        """Set rate limit for platform (default 1 hour)"""
        cache_key = f"{self.rate_limit_cache_prefix}:{platform}"
        cache.set(cache_key, True, duration)
        logger.warning(f"Rate limit set for {platform} for {duration} seconds")
    
    def get_sync_statistics(self, days: int = 7) -> Dict:
        """Get sync statistics for the last N days"""
        since = timezone.now() - timedelta(days=days)
        
        jobs = SyncJob.objects.filter(created_at__gte=since)
        
        stats = {
            'total_jobs': jobs.count(),
            'completed_jobs': jobs.filter(status='completed').count(),
            'failed_jobs': jobs.filter(status='failed').count(),
            'pending_jobs': jobs.filter(status='pending').count(),
            'running_jobs': jobs.filter(status='running').count(),
            'total_accounts_processed': sum(job.accounts_processed for job in jobs),
            'total_accounts_successful': sum(job.accounts_successful for job in jobs),
            'total_accounts_failed': sum(job.accounts_failed for job in jobs),
        }
        
        # Calculate success rate
        if stats['total_accounts_processed'] > 0:
            stats['success_rate'] = (stats['total_accounts_successful'] / stats['total_accounts_processed']) * 100
        else:
            stats['success_rate'] = 0
        
        return stats
    
    def get_account_sync_history(self, account_id: int, limit: int = 50) -> List[Dict]:
        """Get sync history for a specific account"""
        try:
            account = SocialMediaAccount.objects.get(id=account_id)
            history = account.follower_history.all()[:limit]
            
            return [
                {
                    'recorded_at': record.recorded_at,
                    'follower_count': record.follower_count,
                    'following_count': record.following_count,
                    'posts_count': record.posts_count,
                    'engagement_rate': float(record.engagement_rate),
                    'likes_count': record.likes_count,
                    'comments_count': record.comments_count,
                    'views_count': record.views_count,
                }
                for record in history
            ]
        
        except SocialMediaAccount.DoesNotExist:
            return []
    
    def cleanup_old_data(self, days: int = 90):
        """Clean up old sync data"""
        cutoff_date = timezone.now() - timedelta(days=days)
        
        # Delete old follower history (keep recent data)
        old_history = FollowerHistory.objects.filter(recorded_at__lt=cutoff_date)
        deleted_count = old_history.count()
        old_history.delete()
        
        # Delete old completed sync jobs
        old_jobs = SyncJob.objects.filter(
            created_at__lt=cutoff_date,
            status__in=['completed', 'failed', 'cancelled']
        )
        deleted_jobs = old_jobs.count()
        old_jobs.delete()
        
        logger.info(f"Cleaned up {deleted_count} old follower history records and {deleted_jobs} old sync jobs")
        
        return {
            'deleted_history_records': deleted_count,
            'deleted_sync_jobs': deleted_jobs
        }


# Global service instance
sync_service = SocialMediaSyncService()