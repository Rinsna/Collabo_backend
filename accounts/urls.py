from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    RegisterView, LoginView, ProfileView,
    InfluencerProfileView, CompanyProfileView,
    InfluencerListView, InfluencerDetailView, CompanyListView,
    change_password, delete_account, fetch_video_stats, get_video_stats,
    # Admin approval views
    PendingInfluencersListView, AllInfluencersListView, AllUsersListView,
    approve_influencer, reject_influencer, bulk_approve_influencers,
    delete_influencer, approval_stats, mark_approval_shown,
    admin_reset_password
)

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('profile/', ProfileView.as_view(), name='profile'),
    path('influencer-profile/', InfluencerProfileView.as_view(), name='influencer-profile'),
    path('company-profile/', CompanyProfileView.as_view(), name='company-profile'),
    path('influencers/', InfluencerListView.as_view(), name='influencers-list'),
    path('influencers/<int:id>/', InfluencerDetailView.as_view(), name='influencer-detail'),
    path('companies/', CompanyListView.as_view(), name='companies-list'),
    path('change-password/', change_password, name='change-password'),
    path('delete-account/', delete_account, name='delete-account'),
    path('fetch-video-stats/', fetch_video_stats, name='fetch-video-stats'),
    path('get-video-stats/', get_video_stats, name='get-video-stats'),
    
    # Admin approval endpoints
    path('admin/pending-influencers/', PendingInfluencersListView.as_view(), name='pending-influencers'),
    path('admin/all-influencers/', AllInfluencersListView.as_view(), name='all-influencers'),
    path('admin/all-users/', AllUsersListView.as_view(), name='all-users'),
    path('admin/approve-influencer/<int:user_id>/', approve_influencer, name='approve-influencer'),
    path('admin/reject-influencer/<int:user_id>/', reject_influencer, name='reject-influencer'),
    path('admin/bulk-approve/', bulk_approve_influencers, name='bulk-approve-influencers'),
    path('admin/delete-influencer/<int:user_id>/', delete_influencer, name='delete-influencer'),
    path('admin/approval-stats/', approval_stats, name='approval-stats'),
    
    # Influencer approval status
    path('mark-approval-shown/', mark_approval_shown, name='mark-approval-shown'),
    
    # Admin password reset
    path('admin/reset-password/<int:user_id>/', admin_reset_password, name='admin-reset-password'),
]