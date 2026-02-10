from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from django.shortcuts import get_object_or_404
from django.db import models, transaction
from accounts.models import User
from .models import Campaign, CollaborationRequest, DirectCollaborationRequest, Collaboration, Review
from .serializers import (
    CampaignSerializer, CollaborationRequestSerializer, DirectCollaborationRequestSerializer,
    CollaborationSerializer, ReviewSerializer
)

class CampaignListCreateView(generics.ListCreateAPIView):
    serializer_class = CampaignSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['campaign_type', 'status']
    search_fields = ['title', 'description', 'target_audience']
    ordering_fields = ['budget', 'deadline', 'created_at']
    
    def get_queryset(self):
        # Only companies can see campaigns
        if self.request.user.user_type == 'company':
            return Campaign.objects.filter(company=self.request.user)
        # Influencers should not see any campaigns
        return Campaign.objects.none()
    
    def perform_create(self, serializer):
        print(f"Campaign creation attempt by user: {self.request.user.username} (type: {self.request.user.user_type})")
        print(f"Request data: {self.request.data}")
        
        if self.request.user.user_type != 'company':
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("Only companies can create campaigns")
        serializer.save(company=self.request.user)

class CampaignDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = CampaignSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        if self.request.user.user_type == 'company':
            return Campaign.objects.filter(company=self.request.user)
        return Campaign.objects.all()

class DirectCollaborationRequestListCreateView(generics.ListCreateAPIView):
    serializer_class = DirectCollaborationRequestSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        if user.user_type == 'influencer':
            return DirectCollaborationRequest.objects.filter(influencer=user)
        elif user.user_type == 'company':
            return DirectCollaborationRequest.objects.filter(company=user)
        return DirectCollaborationRequest.objects.none()
    
    def perform_create(self, serializer):
        print(f"Direct collaboration request creation by: {self.request.user.username} (type: {self.request.user.user_type})")
        
        if self.request.user.user_type != 'company':
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("Only companies can send collaboration requests")
        
        # Get influencer from the request data
        influencer_id = self.request.data.get('influencer')
        if not influencer_id:
            from rest_framework.exceptions import ValidationError
            raise ValidationError("Influencer ID is required")
        
        influencer = get_object_or_404(User, id=influencer_id, user_type='influencer')
        
        serializer.save(
            company=self.request.user,
            influencer=influencer
        )

class DirectCollaborationRequestDetailView(generics.RetrieveUpdateAPIView):
    serializer_class = DirectCollaborationRequestSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        if user.user_type == 'influencer':
            return DirectCollaborationRequest.objects.filter(influencer=user)
        elif user.user_type == 'company':
            return DirectCollaborationRequest.objects.filter(company=user)
        return DirectCollaborationRequest.objects.none()

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def accept_direct_collaboration_request(request, pk):
    """Accept a direct collaboration request"""
    direct_request = get_object_or_404(
        DirectCollaborationRequest, 
        pk=pk, 
        influencer=request.user
    )
    
    if direct_request.status != 'pending':
        return Response(
            {'error': 'Request is not pending'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    direct_request.status = 'accepted'
    direct_request.save()
    
    # Parse dates and make them timezone-aware
    from django.utils import timezone
    from datetime import datetime, timedelta
    
    start_date_str = request.data.get('start_date')
    end_date_str = request.data.get('end_date')
    
    try:
        if start_date_str:
            start_date = timezone.make_aware(datetime.strptime(start_date_str, '%Y-%m-%d'))
        else:
            start_date = timezone.now()
            
        if end_date_str:
            end_date = timezone.make_aware(datetime.strptime(end_date_str, '%Y-%m-%d'))
        else:
            end_date = timezone.now() + timedelta(days=30)
    except ValueError as e:
        return Response(
            {'error': f'Invalid date format. Use YYYY-MM-DD. Error: {str(e)}'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Create collaboration
    Collaboration.objects.create(
        direct_request=direct_request,
        start_date=start_date,
        end_date=end_date,
        final_rate=direct_request.proposed_rate or 0
    )
    
    return Response({'message': 'Direct collaboration request accepted successfully'})

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def reject_direct_collaboration_request(request, pk):
    """Reject a direct collaboration request"""
    direct_request = get_object_or_404(
        DirectCollaborationRequest, 
        pk=pk, 
        influencer=request.user
    )
    
    if direct_request.status != 'pending':
        return Response(
            {'error': 'Request is not pending'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    direct_request.status = 'rejected'
    direct_request.rejection_reason = request.data.get('rejection_reason', '')
    direct_request.save()
    
    return Response({'message': 'Direct collaboration request rejected'})

class CollaborationRequestListCreateView(generics.ListCreateAPIView):
    serializer_class = CollaborationRequestSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        if user.user_type == 'influencer':
            return CollaborationRequest.objects.filter(influencer=user)
        elif user.user_type == 'company':
            return CollaborationRequest.objects.filter(company=user)
        return CollaborationRequest.objects.none()
    
    def perform_create(self, serializer):
        print(f"Collaboration request creation attempt by user: {self.request.user.username} (type: {self.request.user.user_type})")
        print(f"Request data: {self.request.data}")
        
        # Influencers can no longer apply to campaigns
        from rest_framework.exceptions import PermissionDenied
        raise PermissionDenied({
            "error": "Campaign applications are no longer available",
            "message": "Influencers can only receive direct collaboration requests from companies"
        })

class CollaborationRequestDetailView(generics.RetrieveUpdateAPIView):
    serializer_class = CollaborationRequestSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        if user.user_type == 'influencer':
            return CollaborationRequest.objects.filter(influencer=user)
        elif user.user_type == 'company':
            return CollaborationRequest.objects.filter(company=user)
        return CollaborationRequest.objects.none()

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def accept_collaboration_request(request, pk):
    collaboration_request = get_object_or_404(
        CollaborationRequest, 
        pk=pk, 
        company=request.user
    )
    
    if collaboration_request.status != 'pending':
        return Response(
            {'error': 'Request is not pending'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    collaboration_request.status = 'accepted'
    collaboration_request.save()
    
    # Parse dates and make them timezone-aware
    from django.utils import timezone
    from datetime import datetime, timedelta
    
    start_date_str = request.data.get('start_date')
    end_date_str = request.data.get('end_date')
    
    try:
        if start_date_str:
            start_date = timezone.make_aware(datetime.strptime(start_date_str, '%Y-%m-%d'))
        else:
            start_date = timezone.now()
            
        if end_date_str:
            end_date = timezone.make_aware(datetime.strptime(end_date_str, '%Y-%m-%d'))
        else:
            end_date = timezone.now() + timedelta(days=30)
    except ValueError as e:
        return Response(
            {'error': f'Invalid date format. Use YYYY-MM-DD. Error: {str(e)}'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Create collaboration
    Collaboration.objects.create(
        request=collaboration_request,
        start_date=start_date,
        end_date=end_date,
        final_rate=collaboration_request.proposed_rate
    )
    
    return Response({'message': 'Request accepted successfully'})

class CollaborationListView(generics.ListAPIView):
    serializer_class = CollaborationSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        if user.user_type == 'influencer':
            return Collaboration.objects.filter(
                models.Q(request__influencer=user) | models.Q(direct_request__influencer=user)
            )
        elif user.user_type == 'company':
            return Collaboration.objects.filter(
                models.Q(request__company=user) | models.Q(direct_request__company=user)
            )
        return Collaboration.objects.all()

class CollaborationDetailView(generics.RetrieveUpdateAPIView):
    serializer_class = CollaborationSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        if user.user_type == 'influencer':
            return Collaboration.objects.filter(
                models.Q(request__influencer=user) | models.Q(direct_request__influencer=user)
            )
        elif user.user_type == 'company':
            return Collaboration.objects.filter(
                models.Q(request__company=user) | models.Q(direct_request__company=user)
            )
        return Collaboration.objects.all()

class ReviewListCreateView(generics.ListCreateAPIView):
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Review.objects.filter(reviewee=self.request.user)
    
    def perform_create(self, serializer):
        collaboration = get_object_or_404(
            Collaboration, 
            id=self.request.data.get('collaboration')
        )
        
        # Determine reviewee based on reviewer
        if collaboration.request:
            if self.request.user == collaboration.request.influencer:
                reviewee = collaboration.request.company
            else:
                reviewee = collaboration.request.influencer
        elif collaboration.direct_request:
            if self.request.user == collaboration.direct_request.influencer:
                reviewee = collaboration.direct_request.company
            else:
                reviewee = collaboration.direct_request.influencer
        else:
            from rest_framework.exceptions import ValidationError
            raise ValidationError("Invalid collaboration")
            
        serializer.save(reviewer=self.request.user, reviewee=reviewee)

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def mark_payment_completed(request, pk):
    """
    Mark campaign payment as completed.
    Move amount from pending payment to total spend.
    """
    campaign = get_object_or_404(Campaign, pk=pk, company=request.user)
    
    # Validate campaign status
    if campaign.status != 'completed':
        return Response(
            {'error': 'Campaign must be completed before marking payment as completed'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Validate payment status
    if campaign.payment_status == 'paid':
        return Response(
            {'error': 'Payment has already been marked as completed'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    company_profile = request.user.company_profile
    
    # Validate pending payment balance
    if company_profile.pending_payment < campaign.budget:
        return Response(
            {'error': 'Insufficient pending payment balance'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Update payment status and balances atomically
    with transaction.atomic():
        # Update campaign payment status
        campaign.payment_status = 'paid'
        campaign.save()
        
        # Move amount from pending to total spend
        company_profile.pending_payment -= campaign.budget
        company_profile.total_spend += campaign.budget
        company_profile.save()
    
    return Response({
        'message': 'Payment marked as completed successfully',
        'campaign': CampaignSerializer(campaign).data,
        'pending_payment': float(company_profile.pending_payment),
        'total_spend': float(company_profile.total_spend)
    })