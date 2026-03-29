"""
Social Media URL Configuration
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from . import analytics_views

# Create router for ViewSets
router = DefaultRouter()
router.register(r'accounts', views.SocialMediaAccountViewSet, basename='social-accounts')

urlpatterns = [
    # ViewSet routes
    path('', include(router.urls)),
    
    # OAuth and connection endpoints
    path('connect/', views.ConnectSocialAccountView.as_view(), name='connect-account'),
    
    # Sync endpoints
    path('sync/user/', views.sync_user_accounts, name='sync-user-accounts'),
    path('sync/status/<str:task_id>/', views.sync_status, name='sync-status'),
    
    # Real-time Analytics endpoints
    path('analytics/company/', analytics_views.get_company_analytics, name='company-analytics'),
    path('analytics/influencer/', analytics_views.get_influencer_analytics, name='influencer-analytics'),
    path('analytics/refresh/', analytics_views.refresh_analytics_data, name='refresh-analytics'),
    
    # Statistics endpoints
    path('stats/follower/', views.follower_stats, name='follower-stats'),
    path('stats/sync/', views.sync_history, name='sync-history'),
    path('stats/admin/', views.admin_sync_stats, name='admin-sync-stats'),
    
    # Public lookup endpoints
    path('lookup/instagram/', views.lookup_instagram_user, name='lookup-instagram'),
    path('lookup/youtube/', views.lookup_youtube_channel, name='lookup-youtube'),
    path('lookup/bulk/', views.bulk_lookup_influencers, name='bulk-lookup'),
    path('search/influencers/', views.search_influencers, name='search-influencers'),
    
    # Webhook endpoints
    path('webhooks/<str:platform>/', views.WebhookView.as_view(), name='webhook'),
    
    # Legacy endpoints for backward compatibility
    path('update-followers/', views.update_my_followers, name='update-followers'),
    path('update-followers-sync/', views.update_followers_sync, name='update-followers-sync'),
    path('follower-stats/', views.get_follower_stats, name='follower-stats-legacy'),
]