from django.db import models
from accounts.models import User, InfluencerProfile, CompanyProfile

class Campaign(models.Model):
    CAMPAIGN_TYPES = (
        ('sponsored_post', 'Sponsored Post'),
        ('product_review', 'Product Review'),
        ('brand_ambassador', 'Brand Ambassador'),
        ('event_coverage', 'Event Coverage'),
        ('giveaway', 'Giveaway'),
    )
    
    STATUS_CHOICES = (
        ('draft', 'Draft'),
        ('active', 'Active'),
        ('paused', 'Paused'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    )
    
    PAYMENT_STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('paid', 'Paid'),
    )
    
    company = models.ForeignKey(User, on_delete=models.CASCADE, related_name='campaigns')
    title = models.CharField(max_length=200)
    description = models.TextField()
    campaign_type = models.CharField(max_length=20, choices=CAMPAIGN_TYPES)
    budget = models.DecimalField(max_digits=10, decimal_places=2)
    target_audience = models.CharField(max_length=200)
    requirements = models.TextField()
    deliverables = models.TextField()
    deadline = models.DateTimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending')
    payment_added_to_pending = models.BooleanField(default=False, help_text="Track if payment was added to pending balance")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.title} - {self.company.username}"

class DirectCollaborationRequest(models.Model):
    """Direct collaboration request from company to influencer without pre-existing campaign"""
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
        ('cancelled', 'Cancelled'),
    )
    
    company = models.ForeignKey(User, on_delete=models.CASCADE, related_name='direct_requests_sent')
    influencer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='direct_requests_received')
    
    # Basic info
    message = models.TextField()
    proposed_rate = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    # Campaign details (stored as JSON for flexibility)
    campaign_details = models.JSONField(default=dict, blank=True)
    
    # Status and timestamps
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    rejection_reason = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['company', 'influencer', 'created_at']
        ordering = ['-created_at']
    
    def __str__(self):
        campaign_title = self.campaign_details.get('title', 'Untitled Campaign')
        return f"{campaign_title} - {self.company.username} to {self.influencer.username}"

class CollaborationRequest(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    )
    
    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE, related_name='requests')
    influencer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='collaboration_requests')
    company = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_requests')
    message = models.TextField(blank=True)
    proposed_rate = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    rejection_reason = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['campaign', 'influencer']
    
    def __str__(self):
        return f"{self.campaign.title} - {self.influencer.username}"

class Collaboration(models.Model):
    STATUS_CHOICES = (
        ('in_progress', 'In Progress'),
        ('submitted', 'Submitted'),
        ('approved', 'Approved'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    )
    
    request = models.OneToOneField(CollaborationRequest, on_delete=models.CASCADE, null=True, blank=True)
    direct_request = models.OneToOneField(DirectCollaborationRequest, on_delete=models.CASCADE, null=True, blank=True)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    final_rate = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='in_progress')
    deliverable_urls = models.JSONField(default=list, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        if self.request:
            return f"Collaboration: {self.request.campaign.title}"
        elif self.direct_request:
            campaign_title = self.direct_request.campaign_details.get('title', 'Direct Collaboration')
            return f"Collaboration: {campaign_title}"
        return f"Collaboration #{self.id}"

class Review(models.Model):
    RATING_CHOICES = [(i, i) for i in range(1, 6)]
    
    collaboration = models.OneToOneField(Collaboration, on_delete=models.CASCADE)
    reviewer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='given_reviews')
    reviewee = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_reviews')
    rating = models.IntegerField(choices=RATING_CHOICES)
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Review by {self.reviewer.username} for {self.reviewee.username}"