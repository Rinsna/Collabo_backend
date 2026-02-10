from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    RegisterView, LoginView, ProfileView,
    InfluencerProfileView, CompanyProfileView,
    InfluencerListView, InfluencerDetailView, CompanyListView,
    change_password, delete_account, fetch_video_stats, get_video_stats
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
]