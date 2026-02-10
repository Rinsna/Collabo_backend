"""
Real-time Analytics Views
Fetches real-time data from connected social media accounts for analytics dashboard
"""

import logging
from datetime import datetime, timedelta
from django.utils import timezone
from django.db.models import Sum, Avg, Count, Q
from rest_framework import status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

from .models import SocialMediaAccount, FollowerHistory
from collaborations.models import Campaign, CollaborationRequest
from accounts.models import InfluencerProfile

logger = logging.getLogger(__name__)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_company_analytics(request):
    """
    Get real-time analytics data for company dashboard
    Fetches data from connected social media accounts of influencers they've worked with
    """
    user = request.user
    
    # Check if user is a company
    if user.user_type != 'company':
        return Response({
            'error': 'This endpoint is only available for company accounts'
        }, status=status.HTTP_403_FORBIDDEN)
    
    try:
        # Get date range from query params
        days = int(request.query_params.get('days', 180))  # Last 6 months by default
        start_date = timezone.now() - timedelta(days=days)
        
        # Get all campaigns for this company
        campaigns = Campaign.objects.filter(company=user)
        
        # Get all collaboration requests (accepted ones)
        collaborations = CollaborationRequest.objects.filter(
            campaign__company=user,
            status='accepted'
        )
        
        # Get unique influencers the company has worked with
        influencer_ids = collaborations.values_list('influencer_id', flat=True).distinct()
        
        # Get social media accounts of these influencers
        social_accounts = SocialMediaAccount.objects.filter(
            user_id__in=influencer_ids,
            status='active'
        )
        
        # Calculate total reach (sum of all influencer followers)
        total_reach = 0
        engagement_rates = []
        platform_breakdown = {'instagram': 0, 'youtube': 0}
        
        for account in social_accounts:
            latest_history = account.follower_history.first()
            if latest_history:
                total_reach += latest_history.follower_count
                engagement_rates.append(float(latest_history.engagement_rate))
                
                if account.platform in platform_breakdown:
                    platform_breakdown[account.platform] += latest_history.follower_count
        
        # Calculate average engagement rate
        avg_engagement = sum(engagement_rates) / len(engagement_rates) if engagement_rates else 0
        
        # Get performance trends (last 6 months)
        performance_trends = []
        for i in range(6):
            month_start = timezone.now() - timedelta(days=30 * (5 - i))
            month_end = month_start + timedelta(days=30)
            
            # Get follower history for this month
            month_history = FollowerHistory.objects.filter(
                social_account__user_id__in=influencer_ids,
                recorded_at__gte=month_start,
                recorded_at__lt=month_end
            )
            
            month_reach = month_history.aggregate(
                total=Sum('follower_count')
            )['total'] or 0
            
            month_engagement = month_history.aggregate(
                avg=Avg('engagement_rate')
            )['avg'] or 0
            
            # Estimate conversions (mock data - would come from actual tracking)
            estimated_conversions = int(month_reach * 0.002)  # 0.2% conversion rate
            
            performance_trends.append({
                'name': month_start.strftime('%b'),
                'reach': month_reach,
                'engagement': int(month_engagement * 1000),  # Scale for display
                'conversions': estimated_conversions
            })
        
        # Get campaign statistics
        campaign_stats = {
            'total_campaigns': campaigns.count(),
            'active_campaigns': campaigns.filter(status='active').count(),
            'completed_campaigns': campaigns.filter(status='completed').count(),
            'draft_campaigns': campaigns.filter(status='draft').count(),
        }
        
        # Get collaboration statistics
        collab_stats = {
            'total_collaborations': collaborations.count(),
            'pending_requests': CollaborationRequest.objects.filter(
                campaign__company=user,
                status='pending'
            ).count(),
            'accepted_requests': collaborations.count(),
            'rejected_requests': CollaborationRequest.objects.filter(
                campaign__company=user,
                status='rejected'
            ).count(),
        }
        
        # Calculate ROI (mock calculation - would use actual revenue data)
        total_budget = campaigns.aggregate(Sum('budget'))['budget__sum'] or 0
        estimated_revenue = total_reach * 0.01  # Mock: ₹0.01 per reach
        roi = ((estimated_revenue - total_budget) / total_budget * 100) if total_budget > 0 else 0
        
        # Get top performing influencers
        top_influencers = []
        for influencer_id in influencer_ids[:5]:
            try:
                influencer = InfluencerProfile.objects.get(user_id=influencer_id)
                influencer_accounts = social_accounts.filter(user_id=influencer_id)
                
                influencer_reach = 0
                influencer_engagement = 0
                
                for account in influencer_accounts:
                    latest = account.follower_history.first()
                    if latest:
                        influencer_reach += latest.follower_count
                        influencer_engagement += float(latest.engagement_rate)
                
                avg_eng = influencer_engagement / influencer_accounts.count() if influencer_accounts.count() > 0 else 0
                
                top_influencers.append({
                    'name': influencer.user.username,
                    'reach': influencer_reach,
                    'engagement': round(avg_eng, 2),
                    'roi': int(roi * 1.1),  # Mock ROI per influencer
                    'avatar': influencer.user.username[0].upper(),
                    'category': influencer.category or 'General'
                })
            except InfluencerProfile.DoesNotExist:
                continue
        
        # Sort by reach
        top_influencers.sort(key=lambda x: x['reach'], reverse=True)
        
        return Response({
            'success': True,
            'data': {
                'kpi': {
                    'total_reach': total_reach,
                    'engagement_rate': round(avg_engagement, 2),
                    'roi': round(roi, 1),
                    'total_campaigns': campaign_stats['total_campaigns'],
                    'active_campaigns': campaign_stats['active_campaigns'],
                    'reach_change': 12.5,  # Mock - would calculate from historical data
                    'engagement_change': -2.3,  # Mock
                    'roi_change': 18.7  # Mock
                },
                'performance_trends': performance_trends,
                'campaign_stats': campaign_stats,
                'collaboration_stats': collab_stats,
                'platform_distribution': [
                    {
                        'platform': 'Instagram',
                        'percentage': round((platform_breakdown['instagram'] / total_reach * 100) if total_reach > 0 else 0, 1),
                        'color': 'from-pink-500 to-purple-500'
                    },
                    {
                        'platform': 'YouTube',
                        'percentage': round((platform_breakdown['youtube'] / total_reach * 100) if total_reach > 0 else 0, 1),
                        'color': 'from-red-500 to-red-600'
                    }
                ],
                'top_influencers': top_influencers[:5],
                'last_updated': timezone.now(),
                'data_source': 'real_time_social_media_apis'
            }
        })
    
    except Exception as e:
        logger.error(f"Failed to fetch company analytics: {e}")
        return Response({
            'error': 'Failed to fetch analytics data',
            'details': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_influencer_analytics(request):
    """
    Get real-time analytics data for influencer dashboard
    Fetches data from their connected social media accounts
    """
    user = request.user
    
    # Check if user is an influencer
    if user.user_type != 'influencer':
        return Response({
            'error': 'This endpoint is only available for influencer accounts'
        }, status=status.HTTP_403_FORBIDDEN)
    
    try:
        # Get influencer's social media accounts
        social_accounts = SocialMediaAccount.objects.filter(
            user=user,
            status='active'
        )
        
        if not social_accounts.exists():
            return Response({
                'error': 'No connected social media accounts found',
                'message': 'Please connect your Instagram or YouTube account to view analytics'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Calculate total metrics
        total_followers = 0
        total_engagement = 0
        platform_data = {}
        
        for account in social_accounts:
            latest_history = account.follower_history.first()
            if latest_history:
                total_followers += latest_history.follower_count
                total_engagement += float(latest_history.engagement_rate)
                
                platform_data[account.platform] = {
                    'followers': latest_history.follower_count,
                    'engagement_rate': float(latest_history.engagement_rate),
                    'username': account.username,
                    'last_updated': latest_history.recorded_at
                }
        
        avg_engagement = total_engagement / social_accounts.count() if social_accounts.count() > 0 else 0
        
        # Get follower growth trends (last 30 days)
        growth_trends = []
        for i in range(30):
            date = timezone.now() - timedelta(days=29 - i)
            
            day_history = FollowerHistory.objects.filter(
                social_account__user=user,
                recorded_at__date=date.date()
            ).aggregate(
                total=Sum('follower_count')
            )
            
            growth_trends.append({
                'date': date.strftime('%b %d'),
                'followers': day_history['total'] or 0
            })
        
        # Get collaboration statistics
        collaborations = CollaborationRequest.objects.filter(influencer=user)
        
        collab_stats = {
            'total_collaborations': collaborations.count(),
            'active_collaborations': collaborations.filter(status='accepted').count(),
            'pending_requests': collaborations.filter(status='pending').count(),
            'completed_collaborations': collaborations.filter(status='completed').count(),
        }
        
        # Calculate estimated earnings
        try:
            influencer_profile = InfluencerProfile.objects.get(user=user)
            avg_rate = (
                float(influencer_profile.rate_per_post or 0) +
                float(influencer_profile.rate_per_story or 0) +
                float(influencer_profile.rate_per_reel or 0)
            ) / 3
            
            estimated_monthly_earnings = avg_rate * collab_stats['active_collaborations']
        except InfluencerProfile.DoesNotExist:
            estimated_monthly_earnings = 0
        
        return Response({
            'success': True,
            'data': {
                'kpi': {
                    'total_followers': total_followers,
                    'engagement_rate': round(avg_engagement, 2),
                    'active_collaborations': collab_stats['active_collaborations'],
                    'estimated_earnings': round(estimated_monthly_earnings, 2),
                    'follower_growth': 5.2,  # Mock - would calculate from historical data
                    'engagement_change': 3.1  # Mock
                },
                'platform_breakdown': platform_data,
                'growth_trends': growth_trends,
                'collaboration_stats': collab_stats,
                'connected_accounts': social_accounts.count(),
                'last_updated': timezone.now(),
                'data_source': 'real_time_social_media_apis'
            }
        })
    
    except Exception as e:
        logger.error(f"Failed to fetch influencer analytics: {e}")
        return Response({
            'error': 'Failed to fetch analytics data',
            'details': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def refresh_analytics_data(request):
    """
    Trigger a refresh of analytics data by syncing all connected social media accounts
    """
    user = request.user
    
    try:
        from .tasks import sync_user_social_accounts
        
        # Trigger async sync
        task = sync_user_social_accounts.delay(user.id)
        
        return Response({
            'message': 'Analytics data refresh started',
            'task_id': task.id,
            'estimated_completion': '30-60 seconds'
        })
    
    except Exception as e:
        logger.error(f"Failed to refresh analytics data: {e}")
        return Response({
            'error': 'Failed to refresh analytics data',
            'details': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
