from rest_framework import generics, status, permissions, filters
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from django.contrib.auth.hashers import check_password
from django.utils import timezone
from .models import User, InfluencerProfile, CompanyProfile
from .serializers import (
    UserRegistrationSerializer, UserLoginSerializer, 
    UserSerializer, InfluencerProfileSerializer, CompanyProfileSerializer,
    ChangePasswordSerializer, PendingInfluencerSerializer, ApprovalActionSerializer
)
from .youtube_service import VideoStatsService

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [AllowAny]
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        # Create profile based on user type
        if user.user_type == 'influencer':
            profile_data = {
                'bio': request.data.get('bio', ''),
                'category': request.data.get('category', ''),
                'preferred_platforms': request.data.get('preferred_platforms', []),
            }
            profile = InfluencerProfile.objects.create(user=user, **profile_data)
            
            # Auto-create social media accounts if handles provided
            self._auto_create_social_accounts_on_register(user, request.data)
            
        elif user.user_type == 'company':
            CompanyProfile.objects.create(user=user)
        
        # Generate tokens
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'user': UserSerializer(user).data,
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }, status=status.HTTP_201_CREATED)
    
    def _auto_create_social_accounts_on_register(self, user, data):
        """
        Auto-create social media accounts during registration
        """
        from social_media.models import SocialMediaAccount
        from django.utils import timezone
        import logging
        
        logger = logging.getLogger(__name__)
        
        # Handle Instagram
        instagram_handle = data.get('instagram_handle', '').strip().lstrip('@')
        if instagram_handle:
            try:
                SocialMediaAccount.objects.create(
                    user=user,
                    platform='instagram',
                    platform_user_id=instagram_handle,
                    username=instagram_handle,
                    encrypted_access_token='auto_created',
                    status='active',
                    connected_at=timezone.now()
                )
                logger.info(f"Instagram account created during registration for {user.username}")
            except Exception as e:
                logger.error(f"Failed to create Instagram account during registration: {e}")
        
        # Handle YouTube
        youtube_channel = data.get('youtube_channel', '').strip().lstrip('@')
        if youtube_channel:
            try:
                SocialMediaAccount.objects.create(
                    user=user,
                    platform='youtube',
                    platform_user_id=youtube_channel,
                    username=youtube_channel,
                    encrypted_access_token='auto_created',
                    status='active',
                    connected_at=timezone.now()
                )
                logger.info(f"YouTube account created during registration for {user.username}")
            except Exception as e:
                logger.error(f"Failed to create YouTube account during registration: {e}")

class LoginView(generics.GenericAPIView):
    serializer_class = UserLoginSerializer
    permission_classes = [AllowAny]
    
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'user': UserSerializer(user).data,
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        })

class ProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    
    def get_object(self):
        return self.request.user

class InfluencerProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = InfluencerProfileSerializer
    permission_classes = [IsAuthenticated]
    
    def get_object(self):
        profile, created = InfluencerProfile.objects.get_or_create(user=self.request.user)
        return profile
    
    def update(self, request, *args, **kwargs):
        # Log the incoming data for debugging
        import logging
        logger = logging.getLogger(__name__)
        logger.info(f"Received data: {request.data}")
        
        try:
            response = super().update(request, *args, **kwargs)
            
            # Auto-create social media accounts after successful profile update
            self._auto_create_social_accounts(request)
            
            return response
        except Exception as e:
            logger.error(f"Update error: {str(e)}")
            raise
    
    def _auto_create_social_accounts(self, request):
        """
        Automatically create or update social media account connections
        based on profile data (Instagram handle, YouTube channel)
        """
        from social_media.models import SocialMediaAccount
        from django.utils import timezone
        import logging
        
        logger = logging.getLogger(__name__)
        user = request.user
        profile = self.get_object()
        
        # Handle Instagram
        instagram_handle = request.data.get('instagram_handle') or profile.instagram_handle
        if instagram_handle:
            instagram_handle = instagram_handle.strip().lstrip('@')
            if instagram_handle:
                try:
                    account, created = SocialMediaAccount.objects.get_or_create(
                        user=user,
                        platform='instagram',
                        defaults={
                            'platform_user_id': instagram_handle,
                            'username': instagram_handle,
                            'encrypted_access_token': 'auto_created',
                            'status': 'active',
                            'connected_at': timezone.now()
                        }
                    )
                    if not created:
                        # Update existing account
                        account.username = instagram_handle
                        account.platform_user_id = instagram_handle
                        account.status = 'active'
                        account.save()
                    
                    logger.info(f"Instagram account {'created' if created else 'updated'} for user {user.username}")
                    
                    # Create initial follower history if needed
                    if created and profile.followers_count:
                        from social_media.models import FollowerHistory
                        FollowerHistory.objects.create(
                            social_account=account,
                            follower_count=profile.followers_count,
                            engagement_rate=profile.engagement_rate or 0,
                            sync_source='profile_data'
                        )
                except Exception as e:
                    logger.error(f"Failed to create Instagram account: {e}")
        
        # Handle YouTube
        youtube_channel = request.data.get('youtube_channel') or profile.youtube_channel
        if youtube_channel:
            youtube_channel = youtube_channel.strip().lstrip('@')
            if youtube_channel:
                try:
                    account, created = SocialMediaAccount.objects.get_or_create(
                        user=user,
                        platform='youtube',
                        defaults={
                            'platform_user_id': youtube_channel,
                            'username': youtube_channel,
                            'encrypted_access_token': 'auto_created',
                            'status': 'active',
                            'connected_at': timezone.now()
                        }
                    )
                    if not created:
                        # Update existing account
                        account.username = youtube_channel
                        account.platform_user_id = youtube_channel
                        account.status = 'active'
                        account.save()
                    
                    logger.info(f"YouTube account {'created' if created else 'updated'} for user {user.username}")
                    
                    # Create initial follower history if needed
                    if created and profile.followers_count:
                        from social_media.models import FollowerHistory
                        FollowerHistory.objects.create(
                            social_account=account,
                            follower_count=profile.followers_count,
                            engagement_rate=profile.engagement_rate or 0,
                            sync_source='profile_data'
                        )
                except Exception as e:
                    logger.error(f"Failed to create YouTube account: {e}")

class CompanyProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = CompanyProfileSerializer
    permission_classes = [IsAuthenticated]
    
    def get_object(self):
        profile, created = CompanyProfile.objects.get_or_create(user=self.request.user)
        return profile

class InfluencerListView(generics.ListAPIView):
    queryset = InfluencerProfile.objects.all()
    serializer_class = InfluencerProfileSerializer
    permission_classes = [AllowAny]  # Allow public access for landing page
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['user__username', 'bio', 'category']
    ordering_fields = ['followers_count', 'engagement_rate', 'rate_per_post']
    ordering = ['-followers_count']  # Default ordering
    
    def get_queryset(self):
        # Only return APPROVED influencer profiles
        # This ensures only approved influencers appear on landing page and company searches
        queryset = super().get_queryset().filter(
            user__user_type='influencer',
            user__approval_status='approved'
        )
        category = self.request.query_params.get('category', None)
        if category:
            queryset = queryset.filter(category=category)
        return queryset

class InfluencerDetailView(generics.RetrieveAPIView):
    queryset = InfluencerProfile.objects.all()
    serializer_class = InfluencerProfileSerializer
    permission_classes = [AllowAny]  # Allow public access for viewing profiles
    lookup_field = 'id'
    
    def get_queryset(self):
        # Only allow viewing APPROVED influencer profiles
        # Prevents companies from accessing pending/rejected influencer data
        return super().get_queryset().filter(user__approval_status='approved')

class CompanyListView(generics.ListAPIView):
    queryset = CompanyProfile.objects.all()
    serializer_class = CompanyProfileSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['company_name', 'description', 'industry']


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def change_password(request):
    """
    Change user password
    """
    serializer = ChangePasswordSerializer(data=request.data)
    
    if serializer.is_valid():
        user = request.user
        old_password = serializer.validated_data['old_password']
        new_password = serializer.validated_data['new_password']
        
        # Check if old password is correct
        if not check_password(old_password, user.password):
            return Response({
                'old_password': ['Current password is incorrect.']
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Set new password
        user.set_password(new_password)
        user.save()
        
        return Response({
            'message': 'Password updated successfully.'
        }, status=status.HTTP_200_OK)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def delete_account(request):
    """
    Delete user account
    """
    user = request.user
    password = request.data.get('password')
    
    if not password:
        return Response({
            'password': ['Password is required to delete account.']
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Verify password
    if not check_password(password, user.password):
        return Response({
            'password': ['Password is incorrect.']
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Delete the user account
    user.delete()
    
    return Response({
        'message': 'Account deleted successfully.'
    }, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def fetch_video_stats(request):
    """
    Fetch and update video statistics for the current user's profile (YouTube & Instagram)
    """
    try:
        profile = InfluencerProfile.objects.get(user=request.user)
    except InfluencerProfile.DoesNotExist:
        return Response({
            'error': 'Influencer profile not found'
        }, status=status.HTTP_404_NOT_FOUND)
    
    # Update video stats
    updated = VideoStatsService.update_profile_video_stats(profile)
    
    if updated:
        # Return updated profile data
        serializer = InfluencerProfileSerializer(profile)
        return Response({
            'message': 'Video statistics updated successfully',
            'profile': serializer.data
        }, status=status.HTTP_200_OK)
    else:
        return Response({
            'error': 'No video links found or failed to fetch statistics'
        }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_video_stats(request):
    """
    Get video statistics for a specific URL (YouTube or Instagram)
    Query param: url (video URL)
    """
    video_url = request.query_params.get('url')
    
    if not video_url:
        return Response({
            'error': 'Video URL is required'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    stats = VideoStatsService.get_stats(video_url)
    
    if stats:
        return Response(stats, status=status.HTTP_200_OK)
    else:
        return Response({
            'error': 'Failed to fetch video statistics'
        }, status=status.HTTP_400_BAD_REQUEST)


# ============================================
# ADMIN APPROVAL SYSTEM
# ============================================

class PendingInfluencersListView(generics.ListAPIView):
    """
    List all pending influencer accounts awaiting approval
    Only accessible by superadmin
    """
    serializer_class = PendingInfluencerSerializer
    permission_classes = [IsAdminUser]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['username', 'email']
    ordering_fields = ['created_at', 'username']
    ordering = ['-created_at']  # Newest first
    
    def get_queryset(self):
        return User.objects.filter(
            user_type='influencer',
            approval_status='pending'
        ).select_related('influencer_profile')


class AllUsersListView(generics.ListAPIView):
    """
    List all registered users (Influencers and Companies)
    Only accessible by superadmin
    """
    queryset = User.objects.all().exclude(user_type='admin').select_related('influencer_profile', 'company_profile')
    serializer_class = UserSerializer
    permission_classes = [IsAdminUser]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['username', 'email', 'user_type']
    ordering_fields = ['created_at', 'username', 'user_type']
    ordering = ['-created_at']
    
    def get_queryset(self):
        queryset = super().get_queryset()
        user_type = self.request.query_params.get('user_type', None)
        if user_type:
            queryset = queryset.filter(user_type=user_type)
        return queryset

class AllInfluencersListView(generics.ListAPIView):
    """
    List all influencer accounts (pending, approved, rejected)
    Only accessible by superadmin
    """
    serializer_class = PendingInfluencerSerializer
    permission_classes = [IsAdminUser]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['username', 'email']
    ordering_fields = ['created_at', 'username', 'approval_status']
    ordering = ['-created_at']
    
    def get_queryset(self):
        queryset = User.objects.filter(
            user_type='influencer'
        ).select_related('influencer_profile')
        
        # Filter by approval status if provided
        status_filter = self.request.query_params.get('status', None)
        if status_filter in ['pending', 'approved', 'rejected']:
            queryset = queryset.filter(approval_status=status_filter)
        
        return queryset


@api_view(['POST'])
@permission_classes([IsAdminUser])
def approve_influencer(request, user_id):
    """
    Approve a pending influencer account
    """
    from .models import ApprovalAuditLog
    from .email_service import ApprovalEmailService
    import logging
    
    logger = logging.getLogger(__name__)
    
    try:
        user = User.objects.get(id=user_id, user_type='influencer')
    except User.DoesNotExist:
        return Response({
            'error': 'Influencer not found'
        }, status=status.HTTP_404_NOT_FOUND)
    
    if user.approval_status == 'approved':
        return Response({
            'message': 'Influencer is already approved'
        }, status=status.HTTP_200_OK)
    
    # Store previous status for audit log
    previous_status = user.approval_status
    
    # Approve the influencer
    user.is_approved = True
    user.approval_status = 'approved'
    user.approved_at = timezone.now()
    user.approved_by = request.user
    user.rejection_reason = ''  # Clear any previous rejection reason
    user.save()
    
    # Create audit log
    try:
        # Get client IP address
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip_address = x_forwarded_for.split(',')[0]
        else:
            ip_address = request.META.get('REMOTE_ADDR')
        
        ApprovalAuditLog.objects.create(
            user=user,
            admin=request.user,
            action='approved',
            previous_status=previous_status,
            new_status='approved',
            reason='',
            ip_address=ip_address
        )
        logger.info(f"Audit log created for approval of {user.username}")
    except Exception as e:
        logger.error(f"Failed to create audit log: {e}")
    
    # Email sending removed as per requirements
    
    return Response({
        'message': 'Influencer approved successfully',
        'user': PendingInfluencerSerializer(user).data
    }, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAdminUser])
def reject_influencer(request, user_id):
    """
    Reject a pending influencer account
    """
    from .models import ApprovalAuditLog
    from .email_service import ApprovalEmailService
    import logging
    
    logger = logging.getLogger(__name__)
    
    try:
        user = User.objects.get(id=user_id, user_type='influencer')
    except User.DoesNotExist:
        return Response({
            'error': 'Influencer not found'
        }, status=status.HTTP_404_NOT_FOUND)
    
    # Store previous status for audit log
    previous_status = user.approval_status
    
    # Reject the influencer - no rejection reason required
    user.is_approved = False
    user.approval_status = 'rejected'
    user.rejection_reason = None  # Clear any previous rejection reason
    user.approved_at = None
    user.approved_by = None
    user.save()
    
    # Create audit log
    try:
        # Get client IP address
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip_address = x_forwarded_for.split(',')[0]
        else:
            ip_address = request.META.get('REMOTE_ADDR')
        
        ApprovalAuditLog.objects.create(
            user=user,
            admin=request.user,
            action='rejected',
            previous_status=previous_status,
            new_status='rejected',
            reason=rejection_reason,
            ip_address=ip_address
        )
        logger.info(f"Audit log created for rejection of {user.username}")
    except Exception as e:
        logger.error(f"Failed to create audit log: {e}")
    
    # Email sending removed as per requirements
    
    return Response({
        'message': 'Influencer rejected successfully',
        'user': PendingInfluencerSerializer(user).data
    }, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAdminUser])
def bulk_approve_influencers(request):
    """
    Bulk approve multiple influencers
    Expects: { "user_ids": [1, 2, 3, ...] }
    """
    from .models import ApprovalAuditLog
    from .email_service import ApprovalEmailService
    import logging
    
    logger = logging.getLogger(__name__)
    
    user_ids = request.data.get('user_ids', [])
    
    if not user_ids or not isinstance(user_ids, list):
        return Response({
            'error': 'user_ids must be a non-empty list'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    users = User.objects.filter(
        id__in=user_ids,
        user_type='influencer',
        approval_status='pending'
    )
    
    # Get client IP address
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip_address = x_forwarded_for.split(',')[0]
    else:
        ip_address = request.META.get('REMOTE_ADDR')
    
    approved_count = 0
    for user in users:
        previous_status = user.approval_status
        
        user.is_approved = True
        user.approval_status = 'approved'
        user.approved_at = timezone.now()
        user.approved_by = request.user
        user.rejection_reason = ''
        user.save()
        
        # Create audit log
        try:
            ApprovalAuditLog.objects.create(
                user=user,
                admin=request.user,
                action='approved',
                previous_status=previous_status,
                new_status='approved',
                reason='Bulk approval',
                ip_address=ip_address
            )
        except Exception as e:
            logger.error(f"Failed to create audit log for {user.username}: {e}")
        
        # Send approval email
        try:
            ApprovalEmailService.send_approval_email(user)
        except Exception as e:
            logger.error(f"Failed to send approval email to {user.email}: {e}")
        
        approved_count += 1
    
    return Response({
        'message': f'{approved_count} influencer(s) approved successfully',
        'approved_count': approved_count
    }, status=status.HTTP_200_OK)


@api_view(['DELETE'])
@permission_classes([IsAdminUser])
def delete_influencer(request, user_id):
    """
    Delete an influencer account (usually for rejected accounts)
    """
    try:
        user = User.objects.get(id=user_id, user_type='influencer')
    except User.DoesNotExist:
        return Response({
            'error': 'Influencer not found'
        }, status=status.HTTP_404_NOT_FOUND)
    
    username = user.username
    user.delete()
    
    return Response({
        'message': f'Influencer {username} deleted successfully'
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAdminUser])
def approval_stats(request):
    """
    Get statistics about influencer approvals
    """
    total_influencers = User.objects.filter(user_type='influencer').count()
    pending_count = User.objects.filter(user_type='influencer', approval_status='pending').count()
    approved_count = User.objects.filter(user_type='influencer', approval_status='approved').count()
    rejected_count = User.objects.filter(user_type='influencer', approval_status='rejected').count()
    
    return Response({
        'total_influencers': total_influencers,
        'pending': pending_count,
        'approved': approved_count,
        'rejected': rejected_count
    }, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def mark_approval_shown(request):
    """
    Mark that the approval popup has been shown to the user
    """
    user = request.user
    
    if user.user_type != 'influencer':
        return Response({
            'error': 'Only influencers can mark approval as shown'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    if user.approval_status != 'approved':
        return Response({
            'error': 'User is not approved'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    user.approval_shown = True
    user.save()
    
    return Response({
        'message': 'Approval popup marked as shown'
    }, status=status.HTTP_200_OK)