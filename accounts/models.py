from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    USER_TYPES = (
        ('influencer', 'Influencer'),
        ('company', 'Company'),
        ('admin', 'Admin'),
    )
    
    user_type = models.CharField(max_length=20, choices=USER_TYPES)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, blank=True)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'user_type']

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