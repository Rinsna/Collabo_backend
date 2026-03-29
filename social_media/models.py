from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from cryptography.fernet import Fernet
from django.conf import settings
import json

User = get_user_model()

class SocialMediaAccount(models.Model):
    """Model to store social media account connections"""
    
    PLATFORM_CHOICES = (
        ('instagram', 'Instagram'),
        ('youtube', 'YouTube'),
        ('tiktok', 'TikTok'),
        ('twitter', 'Twitter'),
        ('facebook', 'Facebook'),
    )
    
    STATUS_CHOICES = (
        ('active', 'Active'),
        ('expired', 'Expired'),
        ('revoked', 'Revoked'),
        ('error', 'Error'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='social_accounts')
    platform = models.CharField(max_length=20, choices=PLATFORM_CHOICES)
    platform_user_id = models.CharField(max_length=100)  # Platform's user ID
    username = models.CharField(max_length=100)  # Platform username/handle
    display_name = models.CharField(max_length=200, blank=True)
    profile_picture_url = models.URLField(blank=True)
    
    # Encrypted token storage
    encrypted_access_token = models.TextField()
    encrypted_refresh_token = models.TextField(blank=True)
    token_expires_at = models.DateTimeField(null=True, blank=True)
    
    # Account status and metadata
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    scopes = models.JSONField(default=list)  # Permissions granted
    last_sync = models.DateTimeField(null=True, blank=True)
    sync_error_count = models.IntegerField(default=0)
    last_error = models.TextField(blank=True)
    
    # Timestamps
    connected_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['user', 'platform']
        indexes = [
            models.Index(fields=['user', 'platform']),
            models.Index(fields=['status']),
            models.Index(fields=['last_sync']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.platform} (@{self.username})"
    
    def encrypt_token(self, token):
        """Encrypt a token using Fernet encryption"""
        if not token:
            return ""
        
        key = settings.SOCIAL_MEDIA_ENCRYPTION_KEY.encode()
        f = Fernet(key)
        return f.encrypt(token.encode()).decode()
    
    def decrypt_token(self, encrypted_token):
        """Decrypt a token using Fernet encryption"""
        if not encrypted_token:
            return ""
        
        key = settings.SOCIAL_MEDIA_ENCRYPTION_KEY.encode()
        f = Fernet(key)
        return f.decrypt(encrypted_token.encode()).decode()
    
    def set_access_token(self, token):
        """Set and encrypt the access token"""
        self.encrypted_access_token = self.encrypt_token(token)
    
    def get_access_token(self):
        """Get and decrypt the access token"""
        return self.decrypt_token(self.encrypted_access_token)
    
    def set_refresh_token(self, token):
        """Set and encrypt the refresh token"""
        self.encrypted_refresh_token = self.encrypt_token(token)
    
    def get_refresh_token(self):
        """Get and decrypt the refresh token"""
        return self.decrypt_token(self.encrypted_refresh_token)
    
    def is_token_expired(self):
        """Check if the access token is expired"""
        if not self.token_expires_at:
            return False
        return timezone.now() >= self.token_expires_at
    
    def mark_error(self, error_message):
        """Mark account as having an error"""
        self.sync_error_count += 1
        self.last_error = error_message
        if self.sync_error_count >= 5:  # After 5 consecutive errors, mark as error status
            self.status = 'error'
        self.save()
    
    def reset_error_count(self):
        """Reset error count after successful sync"""
        self.sync_error_count = 0
        self.last_error = ""
        if self.status == 'error':
            self.status = 'active'
        self.save()


class FollowerHistory(models.Model):
    """Model to track follower count history"""
    
    social_account = models.ForeignKey(SocialMediaAccount, on_delete=models.CASCADE, related_name='follower_history')
    follower_count = models.PositiveIntegerField()
    following_count = models.PositiveIntegerField(default=0)
    posts_count = models.PositiveIntegerField(default=0)
    engagement_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    
    # Additional metrics
    likes_count = models.PositiveIntegerField(default=0)
    comments_count = models.PositiveIntegerField(default=0)
    shares_count = models.PositiveIntegerField(default=0)
    views_count = models.PositiveIntegerField(default=0)
    
    # Metadata
    recorded_at = models.DateTimeField(auto_now_add=True)
    sync_source = models.CharField(max_length=50, default='api')  # 'api', 'manual', 'webhook'
    
    class Meta:
        indexes = [
            models.Index(fields=['social_account', 'recorded_at']),
            models.Index(fields=['recorded_at']),
        ]
        ordering = ['-recorded_at']
    
    def __str__(self):
        return f"{self.social_account} - {self.follower_count} followers at {self.recorded_at}"


class SyncJob(models.Model):
    """Model to track sync jobs and their status"""
    
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('running', 'Running'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
    )
    
    JOB_TYPE_CHOICES = (
        ('full_sync', 'Full Sync'),
        ('user_sync', 'User Sync'),
        ('platform_sync', 'Platform Sync'),
        ('single_account', 'Single Account'),
    )
    
    job_id = models.CharField(max_length=100, unique=True)
    job_type = models.CharField(max_length=20, choices=JOB_TYPE_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Job parameters
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    platform = models.CharField(max_length=20, blank=True)
    social_account = models.ForeignKey(SocialMediaAccount, on_delete=models.CASCADE, null=True, blank=True)
    
    # Job results
    accounts_processed = models.IntegerField(default=0)
    accounts_successful = models.IntegerField(default=0)
    accounts_failed = models.IntegerField(default=0)
    error_details = models.JSONField(default=dict)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['status', 'created_at']),
            models.Index(fields=['job_type']),
        ]
        ordering = ['-created_at']
    
    def __str__(self):
        return f"SyncJob {self.job_id} - {self.job_type} ({self.status})"
    
    @property
    def duration(self):
        """Calculate job duration"""
        if self.started_at and self.completed_at:
            return self.completed_at - self.started_at
        return None
    
    def mark_started(self):
        """Mark job as started"""
        self.status = 'running'
        self.started_at = timezone.now()
        self.save()
    
    def mark_completed(self):
        """Mark job as completed"""
        self.status = 'completed'
        self.completed_at = timezone.now()
        self.save()
    
    def mark_failed(self, error_details=None):
        """Mark job as failed"""
        self.status = 'failed'
        self.completed_at = timezone.now()
        if error_details:
            self.error_details = error_details
        self.save()


class WebhookEvent(models.Model):
    """Model to store webhook events from social media platforms"""
    
    EVENT_TYPES = (
        ('follower_update', 'Follower Update'),
        ('profile_update', 'Profile Update'),
        ('post_update', 'Post Update'),
        ('account_deauthorized', 'Account Deauthorized'),
    )
    
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('processed', 'Processed'),
        ('failed', 'Failed'),
        ('ignored', 'Ignored'),
    )
    
    platform = models.CharField(max_length=20)
    event_type = models.CharField(max_length=30, choices=EVENT_TYPES)
    platform_user_id = models.CharField(max_length=100)
    
    # Event data
    raw_data = models.JSONField()
    processed_data = models.JSONField(default=dict)
    
    # Processing status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    error_message = models.TextField(blank=True)
    processed_at = models.DateTimeField(null=True, blank=True)
    
    # Timestamps
    received_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['platform', 'platform_user_id']),
            models.Index(fields=['status', 'received_at']),
        ]
        ordering = ['-received_at']
    
    def __str__(self):
        return f"Webhook {self.platform} - {self.event_type} ({self.status})"