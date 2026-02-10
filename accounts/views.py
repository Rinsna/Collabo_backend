from rest_framework import generics, status, permissions, filters
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from django.contrib.auth.hashers import check_password
from .models import User, InfluencerProfile, CompanyProfile
from .serializers import (
    UserRegistrationSerializer, UserLoginSerializer, 
    UserSerializer, InfluencerProfileSerializer, CompanyProfileSerializer,
    ChangePasswordSerializer
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
        # Only return profiles for users with user_type='influencer'
        # This ensures that only actual influencers are displayed in the "Find Influencers" section
        queryset = super().get_queryset().filter(user__user_type='influencer')
        category = self.request.query_params.get('category', None)
        if category:
            queryset = queryset.filter(category=category)
        return queryset

class InfluencerDetailView(generics.RetrieveAPIView):
    queryset = InfluencerProfile.objects.all()
    serializer_class = InfluencerProfileSerializer
    permission_classes = [AllowAny]  # Allow public access for viewing profiles
    lookup_field = 'id'

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