"""
Celery tasks for social media synchronization
"""

from celery import shared_task
from celery.utils.log import get_task_logger
from django.utils import timezone
from datetime import timedelta
from typing import Dict, List

from .sync_service import sync_service
from .models import SocialMediaAccount, SyncJob

logger = get_task_logger(__name__)


@shared_task(bind=True, max_retries=3, default_retry_delay=300)
def sync_all_social_accounts(self):
    """
    Celery task to sync all active social media accounts
    This task should be scheduled to run periodically (e.g., every hour)
    """
    try:
        logger.info("Starting sync_all_social_accounts task")
        job_id = sync_service.sync_all_accounts()
        logger.info(f"Completed sync_all_social_accounts task with job_id: {job_id}")
        return {"status": "success", "job_id": job_id}
    
    except Exception as exc:
        logger.error(f"sync_all_social_accounts task failed: {exc}")
        
        # Retry the task with exponential backoff
        if self.request.retries < self.max_retries:
            retry_delay = 300 * (2 ** self.request.retries)  # Exponential backoff
            logger.info(f"Retrying sync_all_social_accounts in {retry_delay} seconds")
            raise self.retry(countdown=retry_delay, exc=exc)
        
        return {"status": "failed", "error": str(exc)}


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def sync_user_social_accounts(self, user_id: int):
    """
    Celery task to sync social media accounts for a specific user
    """
    try:
        logger.info(f"Starting sync_user_social_accounts task for user {user_id}")
        job_id = sync_service.sync_user_accounts(user_id)
        logger.info(f"Completed sync_user_social_accounts task for user {user_id} with job_id: {job_id}")
        return {"status": "success", "job_id": job_id, "user_id": user_id}
    
    except Exception as exc:
        logger.error(f"sync_user_social_accounts task failed for user {user_id}: {exc}")
        
        if self.request.retries < self.max_retries:
            retry_delay = 60 * (2 ** self.request.retries)
            logger.info(f"Retrying sync_user_social_accounts for user {user_id} in {retry_delay} seconds")
            raise self.retry(countdown=retry_delay, exc=exc)
        
        return {"status": "failed", "error": str(exc), "user_id": user_id}


@shared_task(bind=True, max_retries=2, default_retry_delay=30)
def sync_single_social_account(self, account_id: int):
    """
    Celery task to sync a single social media account
    """
    try:
        logger.info(f"Starting sync_single_social_account task for account {account_id}")
        success = sync_service.sync_single_account_by_id(account_id)
        
        if success:
            logger.info(f"Successfully synced social account {account_id}")
            return {"status": "success", "account_id": account_id}
        else:
            logger.warning(f"Failed to sync social account {account_id}")
            return {"status": "failed", "account_id": account_id, "error": "Sync failed"}
    
    except Exception as exc:
        logger.error(f"sync_single_social_account task failed for account {account_id}: {exc}")
        
        if self.request.retries < self.max_retries:
            retry_delay = 30 * (2 ** self.request.retries)
            logger.info(f"Retrying sync_single_social_account for account {account_id} in {retry_delay} seconds")
            raise self.retry(countdown=retry_delay, exc=exc)
        
        return {"status": "failed", "error": str(exc), "account_id": account_id}


@shared_task
def sync_platform_accounts(platform: str):
    """
    Celery task to sync all accounts for a specific platform
    """
    try:
        logger.info(f"Starting sync_platform_accounts task for platform {platform}")
        
        accounts = SocialMediaAccount.objects.filter(
            platform=platform,
            status='active'
        )
        
        successful_syncs = 0
        failed_syncs = 0
        
        for account in accounts:
            try:
                success = sync_service.sync_single_account_by_id(account.id)
                if success:
                    successful_syncs += 1
                else:
                    failed_syncs += 1
            except Exception as e:
                logger.error(f"Failed to sync account {account.id}: {e}")
                failed_syncs += 1
        
        logger.info(f"Completed sync_platform_accounts for {platform}: {successful_syncs} successful, {failed_syncs} failed")
        
        return {
            "status": "success",
            "platform": platform,
            "successful_syncs": successful_syncs,
            "failed_syncs": failed_syncs
        }
    
    except Exception as exc:
        logger.error(f"sync_platform_accounts task failed for platform {platform}: {exc}")
        return {"status": "failed", "error": str(exc), "platform": platform}


@shared_task
def cleanup_old_sync_data():
    """
    Celery task to clean up old sync data
    This task should be scheduled to run daily
    """
    try:
        logger.info("Starting cleanup_old_sync_data task")
        result = sync_service.cleanup_old_data(days=90)
        logger.info(f"Completed cleanup_old_sync_data task: {result}")
        return {"status": "success", **result}
    
    except Exception as exc:
        logger.error(f"cleanup_old_sync_data task failed: {exc}")
        return {"status": "failed", "error": str(exc)}


@shared_task
def refresh_expired_tokens():
    """
    Celery task to refresh expired access tokens
    This task should be scheduled to run every few hours
    """
    try:
        logger.info("Starting refresh_expired_tokens task")
        
        # Find accounts with tokens expiring in the next 24 hours
        expiry_threshold = timezone.now() + timedelta(hours=24)
        accounts_to_refresh = SocialMediaAccount.objects.filter(
            status='active',
            token_expires_at__lte=expiry_threshold,
            token_expires_at__isnull=False
        )
        
        refreshed_count = 0
        failed_count = 0
        
        for account in accounts_to_refresh:
            try:
                # Use sync service to refresh token
                if sync_service._refresh_account_token(account):
                    refreshed_count += 1
                    logger.info(f"Refreshed token for account {account}")
                else:
                    failed_count += 1
                    logger.warning(f"Failed to refresh token for account {account}")
            
            except Exception as e:
                logger.error(f"Error refreshing token for account {account}: {e}")
                failed_count += 1
        
        logger.info(f"Completed refresh_expired_tokens task: {refreshed_count} refreshed, {failed_count} failed")
        
        return {
            "status": "success",
            "refreshed_count": refreshed_count,
            "failed_count": failed_count
        }
    
    except Exception as exc:
        logger.error(f"refresh_expired_tokens task failed: {exc}")
        return {"status": "failed", "error": str(exc)}


@shared_task
def generate_sync_report():
    """
    Celery task to generate sync statistics report
    This task can be scheduled to run daily for monitoring
    """
    try:
        logger.info("Starting generate_sync_report task")
        
        # Get statistics for the last 7 days
        stats = sync_service.get_sync_statistics(days=7)
        
        # Get account status summary
        account_stats = {
            'total_accounts': SocialMediaAccount.objects.count(),
            'active_accounts': SocialMediaAccount.objects.filter(status='active').count(),
            'expired_accounts': SocialMediaAccount.objects.filter(status='expired').count(),
            'error_accounts': SocialMediaAccount.objects.filter(status='error').count(),
        }
        
        # Get platform breakdown
        platform_stats = {}
        for platform, _ in SocialMediaAccount.PLATFORM_CHOICES:
            platform_stats[platform] = SocialMediaAccount.objects.filter(platform=platform).count()
        
        report = {
            "generated_at": timezone.now().isoformat(),
            "sync_statistics": stats,
            "account_statistics": account_stats,
            "platform_statistics": platform_stats
        }
        
        logger.info(f"Generated sync report: {report}")
        
        return {"status": "success", "report": report}
    
    except Exception as exc:
        logger.error(f"generate_sync_report task failed: {exc}")
        return {"status": "failed", "error": str(exc)}


# Periodic task schedules (to be added to CELERY_BEAT_SCHEDULE in settings)
CELERY_BEAT_SCHEDULE = {
    # Sync all accounts every hour
    'sync-all-social-accounts': {
        'task': 'social_media.tasks.sync_all_social_accounts',
        'schedule': 3600.0,  # Every hour
    },
    
    # Refresh expired tokens every 6 hours
    'refresh-expired-tokens': {
        'task': 'social_media.tasks.refresh_expired_tokens',
        'schedule': 21600.0,  # Every 6 hours
    },
    
    # Clean up old data daily at 2 AM
    'cleanup-old-sync-data': {
        'task': 'social_media.tasks.cleanup_old_sync_data',
        'schedule': 86400.0,  # Daily
    },
    
    # Generate sync report daily at 8 AM
    'generate-sync-report': {
        'task': 'social_media.tasks.generate_sync_report',
        'schedule': 86400.0,  # Daily
    },
}