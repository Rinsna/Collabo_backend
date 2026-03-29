"""
Social Media Serializers
"""

from rest_framework import serializers
from .models import SocialMediaAccount, FollowerHistory, SyncJob, WebhookEvent


class SocialMediaAccountSerializer(serializers.ModelSerializer):
    """Serializer for social media accounts"""
    
    # Don't expose encrypted tokens in API responses
    access_token = serializers.CharField(write_only=True, required=False)
    refresh_token = serializers.CharField(write_only=True, required=False)
    
    # Read-only fields
    is_token_expired = serializers.BooleanField(read_only=True)
    last_sync_ago = serializers.SerializerMethodField()
    follower_count = serializers.SerializerMethodField()
    
    class Meta:
        model = SocialMediaAccount
        fields = [
            'id', 'platform', 'platform_user_id', 'username', 'display_name',
            'profile_picture_url', 'status', 'scopes', 'last_sync', 'sync_error_count',
            'last_error', 'connected_at', 'updated_at', 'token_expires_at',
            'access_token', 'refresh_token', 'is_token_expired', 'last_sync_ago',
            'follower_count'
        ]
        read_only_fields = [
            'id', 'platform_user_id', 'connected_at', 'updated_at', 'sync_error_count',
            'last_error', 'last_sync'
        ]
    
    def get_last_sync_ago(self, obj):
        """Get human-readable time since last sync"""
        if not obj.last_sync:
            return "Never"
        
        from django.utils import timezone
        diff = timezone.now() - obj.last_sync
        
        if diff.days > 0:
            return f"{diff.days} day{'s' if diff.days > 1 else ''} ago"
        elif diff.seconds > 3600:
            hours = diff.seconds // 3600
            return f"{hours} hour{'s' if hours > 1 else ''} ago"
        elif diff.seconds > 60:
            minutes = diff.seconds // 60
            return f"{minutes} minute{'s' if minutes > 1 else ''} ago"
        else:
            return "Just now"
    
    def get_follower_count(self, obj):
        """Get latest follower count"""
        latest_history = obj.follower_history.first()
        return latest_history.follower_count if latest_history else 0
    
    def create(self, validated_data):
        """Create social media account with encrypted tokens"""
        access_token = validated_data.pop('access_token', None)
        refresh_token = validated_data.pop('refresh_token', None)
        
        account = super().create(validated_data)
        
        if access_token:
            account.set_access_token(access_token)
        if refresh_token:
            account.set_refresh_token(refresh_token)
        
        account.save()
        return account
    
    def update(self, instance, validated_data):
        """Update social media account with encrypted tokens"""
        access_token = validated_data.pop('access_token', None)
        refresh_token = validated_data.pop('refresh_token', None)
        
        instance = super().update(instance, validated_data)
        
        if access_token:
            instance.set_access_token(access_token)
        if refresh_token:
            instance.set_refresh_token(refresh_token)
        
        instance.save()
        return instance


class FollowerHistorySerializer(serializers.ModelSerializer):
    """Serializer for follower history records"""
    
    platform = serializers.CharField(source='social_account.platform', read_only=True)
    username = serializers.CharField(source='social_account.username', read_only=True)
    change_from_previous = serializers.SerializerMethodField()
    
    class Meta:
        model = FollowerHistory
        fields = [
            'id', 'follower_count', 'following_count', 'posts_count', 'engagement_rate',
            'likes_count', 'comments_count', 'shares_count', 'views_count',
            'recorded_at', 'sync_source', 'platform', 'username', 'change_from_previous'
        ]
        read_only_fields = ['id', 'recorded_at']
    
    def get_change_from_previous(self, obj):
        """Calculate change from previous record"""
        try:
            previous = FollowerHistory.objects.filter(
                social_account=obj.social_account,
                recorded_at__lt=obj.recorded_at
            ).first()
            
            if previous:
                return obj.follower_count - previous.follower_count
            return 0
        except:
            return 0


class SyncJobSerializer(serializers.ModelSerializer):
    """Serializer for sync jobs"""
    
    duration_seconds = serializers.SerializerMethodField()
    success_rate = serializers.SerializerMethodField()
    
    class Meta:
        model = SyncJob
        fields = [
            'id', 'job_id', 'job_type', 'status', 'accounts_processed',
            'accounts_successful', 'accounts_failed', 'error_details',
            'created_at', 'started_at', 'completed_at', 'duration_seconds',
            'success_rate'
        ]
        read_only_fields = ['id', 'created_at']
    
    def get_duration_seconds(self, obj):
        """Get job duration in seconds"""
        if obj.duration:
            return obj.duration.total_seconds()
        return None
    
    def get_success_rate(self, obj):
        """Calculate success rate percentage"""
        if obj.accounts_processed > 0:
            return round((obj.accounts_successful / obj.accounts_processed) * 100, 2)
        return 0


class WebhookEventSerializer(serializers.ModelSerializer):
    """Serializer for webhook events"""
    
    class Meta:
        model = WebhookEvent
        fields = [
            'id', 'platform', 'event_type', 'platform_user_id', 'raw_data',
            'processed_data', 'status', 'error_message', 'received_at',
            'processed_at'
        ]
        read_only_fields = ['id', 'received_at']


class ConnectAccountSerializer(serializers.Serializer):
    """Serializer for connecting social media accounts"""
    
    platform = serializers.ChoiceField(choices=SocialMediaAccount.PLATFORM_CHOICES)
    auth_code = serializers.CharField(required=False, allow_blank=True)
    access_token = serializers.CharField(required=False, allow_blank=True)
    refresh_token = serializers.CharField(required=False, allow_blank=True)
    expires_in = serializers.IntegerField(required=False, default=3600)
    scopes = serializers.ListField(
        child=serializers.CharField(),
        required=False,
        default=list
    )
    
    def validate(self, data):
        """Validate that either auth_code or access_token is provided"""
        if not data.get('auth_code') and not data.get('access_token'):
            raise serializers.ValidationError(
                "Either 'auth_code' or 'access_token' must be provided"
            )
        return data


class SyncStatsSerializer(serializers.Serializer):
    """Serializer for sync statistics"""
    
    total_jobs = serializers.IntegerField()
    completed_jobs = serializers.IntegerField()
    failed_jobs = serializers.IntegerField()
    pending_jobs = serializers.IntegerField()
    running_jobs = serializers.IntegerField()
    total_accounts_processed = serializers.IntegerField()
    total_accounts_successful = serializers.IntegerField()
    total_accounts_failed = serializers.IntegerField()
    success_rate = serializers.FloatField()


class PlatformStatsSerializer(serializers.Serializer):
    """Serializer for platform-specific statistics"""
    
    followers = serializers.IntegerField()
    engagement_rate = serializers.FloatField()
    last_updated = serializers.DateTimeField()


class FollowerStatsSerializer(serializers.Serializer):
    """Serializer for aggregated follower statistics"""
    
    total_followers = serializers.IntegerField()
    average_engagement_rate = serializers.FloatField()
    connected_accounts = serializers.IntegerField()
    platform_breakdown = serializers.DictField(child=PlatformStatsSerializer())
    last_sync = serializers.DateTimeField(allow_null=True)