from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from accounts.models import InfluencerProfile
import logging

logger = logging.getLogger(__name__)

@receiver(pre_save, sender=InfluencerProfile)
def track_handle_changes(sender, instance, **kwargs):
    """Track changes to social media handles"""
    if instance.pk:  # Only for existing instances
        try:
            old_instance = InfluencerProfile.objects.get(pk=instance.pk)
            
            # Store old values for comparison
            instance._old_instagram_handle = old_instance.instagram_handle
            instance._old_youtube_channel = old_instance.youtube_channel
        except InfluencerProfile.DoesNotExist:
            # New instance
            instance._old_instagram_handle = None
            instance._old_youtube_channel = None
    else:
        # New instance
        instance._old_instagram_handle = None
        instance._old_youtube_channel = None

@receiver(post_save, sender=InfluencerProfile)
def update_followers_on_handle_change_signal(sender, instance, created, **kwargs):
    """Trigger follower update when social media handles change"""
    # Import here to avoid circular imports
    from .tasks import sync_user_social_accounts
    
    if created:
        # New profile created with handles - update followers
        if instance.instagram_handle or instance.youtube_channel:
            logger.info(f"New profile created for {instance.user.username}, triggering sync")
            sync_user_social_accounts.delay(instance.user.id)
    else:
        # Existing profile updated - check for handle changes
        instagram_changed = (
            hasattr(instance, '_old_instagram_handle') and 
            instance._old_instagram_handle != instance.instagram_handle and
            instance.instagram_handle  # Only if new handle is not empty
        )
        
        youtube_changed = (
            hasattr(instance, '_old_youtube_channel') and 
            instance._old_youtube_channel != instance.youtube_channel and
            instance.youtube_channel  # Only if new handle is not empty
        )
        
        if instagram_changed or youtube_changed:
            logger.info(f"Social media handles changed for {instance.user.username}, triggering sync")
            sync_user_social_accounts.delay(instance.user.id)