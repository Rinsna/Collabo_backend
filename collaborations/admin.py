from django.contrib import admin
from .models import Campaign, CollaborationRequest, Collaboration, Review

@admin.register(Campaign)
class CampaignAdmin(admin.ModelAdmin):
    list_display = ('title', 'company', 'campaign_type', 'budget', 'status', 'deadline')
    list_filter = ('campaign_type', 'status', 'created_at')
    search_fields = ('title', 'company__username', 'description')

@admin.register(CollaborationRequest)
class CollaborationRequestAdmin(admin.ModelAdmin):
    list_display = ('campaign', 'influencer', 'company', 'proposed_rate', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('campaign__title', 'influencer__username', 'company__username')

@admin.register(Collaboration)
class CollaborationAdmin(admin.ModelAdmin):
    list_display = ('request', 'final_rate', 'status', 'start_date', 'end_date')
    list_filter = ('status', 'created_at')

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('collaboration', 'reviewer', 'reviewee', 'rating', 'created_at')
    list_filter = ('rating', 'created_at')