from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    USER_TYPES = (
        ('influencer', 'Influencer'),
        ('company', 'Company'),
        ('admin', 'Admin'),
    )
    
    APPROVAL_STATUS = (
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    )
    
    user_type = models.CharField(max_length=20, choices=USER_TYPES)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, blank=True)
    is_verified = models.BooleanField(default=False)
    
    # Approval system for influencers
    is_approved = models.BooleanField(default=False, help_text="Admin approval status for influencers")
    approval_status = models.CharField(max_length=20, choices=APPROVAL_STATUS, default='pending', help_text="Detailed approval status")
    approved_at = models.DateTimeField(null=True, blank=True, help_text="Timestamp when approved by admin")
    approved_by = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL, related_name='approved_users', help_text="Admin who approved this user")
    rejection_reason = models.TextField(blank=True, help_text="Reason for rejection (if applicable)")
    approval_shown = models.BooleanField(default=False, help_text="Whether approval popup has been shown to user")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'user_type']
    
    def save(self, *args, **kwargs):
        # Auto-set approval status for non-influencers
        if self.user_type != 'influencer':
            self.is_approved = True
            self.approval_status = 'approved'
        elif self.user_type == 'influencer' and not self.pk:
            # New influencer registration - set to pending
            self.is_approved = False
            self.approval_status = 'pending'
        
        super().save(*args, **kwargs)


class ApprovalAuditLog(models.Model):
    """Audit log for tracking all approval actions"""
    ACTION_TYPES = (
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('pending', 'Set to Pending'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='approval_logs', help_text="The influencer whose status was changed")
    admin = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='admin_actions', help_text="Admin who performed the action")
    action = models.CharField(max_length=20, choices=ACTION_TYPES, help_text="Type of action performed")
    previous_status = models.CharField(max_length=20, blank=True, help_text="Status before the change")
    new_status = models.CharField(max_length=20, help_text="Status after the change")
    reason = models.TextField(blank=True, help_text="Reason for rejection or notes")
    ip_address = models.GenericIPAddressField(null=True, blank=True, help_text="IP address of admin")
    timestamp = models.DateTimeField(auto_now_add=True, help_text="When the action was performed")
    
    class Meta:
        ordering = ['-timestamp']
        verbose_name = 'Approval Audit Log'
        verbose_name_plural = 'Approval Audit Logs'
    
    def __str__(self):
        return f"{self.admin.username if self.admin else 'System'} {self.action} {self.user.username} at {self.timestamp}"

class InfluencerProfile(models.Model):
    CATEGORY_CHOICES = (
        ('fashion', 'Fashion'),
        ('beauty', 'Beauty'),
        ('fitness', 'Fitness'),
        ('food', 'Food'),
        ('travel', 'Travel'),
        ('tech', 'Technology'),
        ('lifestyle', 'Lifestyle'),
        ('gaming', 'Gaming'),
    )
    
    SOCIAL_MEDIA_PLATFORMS = (
        ('instagram', 'Instagram'),
        ('youtube', 'YouTube')
    )
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='influencer_profile')
    bio = models.TextField(max_length=500, blank=True)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, blank=True)
    preferred_platforms = models.JSONField(default=list, blank=True, help_text="List of preferred social media platforms")
    followers_count = models.PositiveIntegerField(default=0)
    engagement_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    
    # Rates and Costs
    rate_per_post = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, help_text="Rate for a single post")
    rate_per_story = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, help_text="Rate for a story")
    rate_per_reel = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, help_text="Rate for a reel/short video")
    rate_per_video = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, help_text="Rate for a full video")
    
    # Social Media Handles
    instagram_handle = models.CharField(max_length=100, blank=True)
    youtube_channel = models.CharField(max_length=100, blank=True)
    
    # Media and Links
    profile_image = models.TextField(blank=True, help_text="Profile picture URL or base64 data")
    portfolio_images = models.JSONField(default=list, blank=True, help_text="List of portfolio image URLs or base64 data")
    portfolio_videos = models.JSONField(default=list, blank=True, help_text="List of portfolio video URLs or base64 data")
    website_url = models.URLField(blank=True, help_text="Personal website or portfolio")
    latest_product_review_link = models.URLField(blank=True, help_text="Link to latest product review")
    latest_product_review_cover = models.TextField(blank=True, help_text="Cover image URL or base64 data for latest product review")
    latest_product_review_views = models.PositiveIntegerField(default=0, help_text="View count for latest product review")
    latest_product_review_likes = models.PositiveIntegerField(default=0, help_text="Like count for latest product review")
    most_viewed_content_link = models.URLField(blank=True, help_text="Link to most viewed content")
    most_viewed_content_cover = models.TextField(blank=True, help_text="Cover image URL or base64 data for most viewed content")
    most_viewed_content_views = models.PositiveIntegerField(default=0, help_text="View count for most viewed content")
    most_viewed_content_likes = models.PositiveIntegerField(default=0, help_text="Like count for most viewed content")
    
    # Additional Details
    location = models.CharField(max_length=100, blank=True, help_text="City, Country")
    languages = models.JSONField(default=list, blank=True, help_text="Languages spoken")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.category}"

class CompanyProfile(models.Model):
    INDUSTRY_CHOICES = (
        ('fashion', 'Fashion'),
        ('beauty', 'Beauty'),
        ('tech', 'Technology'),
        ('food', 'Food & Beverage'),
        ('fitness', 'Fitness'),
        ('travel', 'Travel'),
        ('automotive', 'Automotive'),
        ('finance', 'Finance'),
    )
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='company_profile')
    company_name = models.CharField(max_length=200)
    description = models.TextField(max_length=1000)
    industry = models.CharField(max_length=20, choices=INDUSTRY_CHOICES)
    website = models.URLField(blank=True)
    company_size = models.CharField(max_length=50, blank=True)
    location = models.CharField(max_length=200, blank=True)
    logo = models.URLField(blank=True)
    
    # Payment tracking
    pending_payment = models.DecimalField(max_digits=12, decimal_places=2, default=0.00, help_text="Total pending payments for completed campaigns")
    total_spend = models.DecimalField(max_digits=12, decimal_places=2, default=0.00, help_text="Total amount spent on paid campaigns")
    
    def __str__(self):
        return self.company_name