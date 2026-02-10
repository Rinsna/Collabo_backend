from django.urls import path
from .views import (
    CampaignListCreateView, CampaignDetailView,
    CollaborationRequestListCreateView, CollaborationRequestDetailView,
    DirectCollaborationRequestListCreateView, DirectCollaborationRequestDetailView,
    CollaborationListView, CollaborationDetailView,
    ReviewListCreateView, accept_collaboration_request,
    accept_direct_collaboration_request, reject_direct_collaboration_request,
    mark_payment_completed
)

urlpatterns = [
    path('campaigns/', CampaignListCreateView.as_view(), name='campaigns'),
    path('campaigns/<int:pk>/', CampaignDetailView.as_view(), name='campaign-detail'),
    path('campaigns/<int:pk>/mark-payment-completed/', mark_payment_completed, name='mark-payment-completed'),
    path('requests/', CollaborationRequestListCreateView.as_view(), name='collaboration-requests'),
    path('requests/<int:pk>/', CollaborationRequestDetailView.as_view(), name='request-detail'),
    path('requests/<int:pk>/accept/', accept_collaboration_request, name='accept-request'),
    path('direct-requests/', DirectCollaborationRequestListCreateView.as_view(), name='direct-requests'),
    path('direct-requests/<int:pk>/', DirectCollaborationRequestDetailView.as_view(), name='direct-request-detail'),
    path('direct-requests/<int:pk>/accept/', accept_direct_collaboration_request, name='accept-direct-request'),
    path('direct-requests/<int:pk>/reject/', reject_direct_collaboration_request, name='reject-direct-request'),
    path('collaborations/', CollaborationListView.as_view(), name='collaborations'),
    path('collaborations/<int:pk>/', CollaborationDetailView.as_view(), name='collaboration-detail'),
    path('reviews/', ReviewListCreateView.as_view(), name='reviews'),
]