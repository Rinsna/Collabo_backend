"""
Social Media API Clients
Handles communication with official social media APIs
"""

import requests
from abc import ABC, abstractmethod
from typing import Dict, Optional, Tuple
from datetime import datetime, timedelta
from django.conf import settings
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)


class BaseSocialMediaClient(ABC):
    """Base class for social media API clients"""
    
    def __init__(self, access_token: str, refresh_token: Optional[str] = None):
        self.access_token = access_token
        self.refresh_token = refresh_token
        self.session = requests.Session()
    
    @abstractmethod
    def get_user_profile(self) -> Dict:
        """Get user profile information"""
        pass
    
    @abstractmethod
    def get_follower_count(self) -> int:
        """Get current follower count"""
        pass
    
    @abstractmethod
    def get_engagement_metrics(self) -> Dict:
        """Get engagement metrics"""
        pass
    
    @abstractmethod
    def refresh_access_token(self) -> Tuple[str, str, datetime]:
        """Refresh the access token"""
        pass
    
    def handle_api_error(self, response: requests.Response, context: str = ""):
        """Handle API errors consistently"""
        try:
            error_data = response.json()
        except:
            error_data = {"error": response.text}
        
        logger.error(f"{self.__class__.__name__} API Error ({context}): {response.status_code} - {error_data}")
        
        if response.status_code == 401:
            raise UnauthorizedError("Access token is invalid or expired")
        elif response.status_code == 403:
            raise ForbiddenError("Insufficient permissions")
        elif response.status_code == 429:
            raise RateLimitError("Rate limit exceeded")
        else:
            raise APIError(f"API request failed: {error_data}")


class InstagramGraphAPIClient(BaseSocialMediaClient):
    """Instagram Graph API Client (for Instagram Business/Creator accounts)"""
    
    BASE_URL = "https://graph.instagram.com"
    GRAPH_URL = "https://graph.facebook.com/v18.0"
    
    def get_user_profile(self) -> Dict:
        """Get Instagram user profile"""
        try:
            url = f"{self.GRAPH_URL}/me"
            params = {
                'fields': 'id,username,name,profile_picture_url,followers_count,follows_count,media_count',
                'access_token': self.access_token
            }
            
            response = self.session.get(url, params=params, timeout=30)
            
            if response.status_code != 200:
                self.handle_api_error(response, "get_user_profile")
            
            return response.json()
        
        except requests.RequestException as e:
            logger.error(f"Instagram API request failed: {e}")
            raise APIError(f"Failed to fetch Instagram profile: {e}")
    
    def get_follower_count(self) -> int:
        """Get Instagram follower count"""
        profile = self.get_user_profile()
        return profile.get('followers_count', 0)
    
    def get_engagement_metrics(self) -> Dict:
        """Get Instagram engagement metrics"""
        try:
            # Get user profile first
            profile = self.get_user_profile()
            user_id = profile.get('id')
            
            # Get recent media
            media_url = f"{self.GRAPH_URL}/{user_id}/media"
            media_params = {
                'fields': 'id,like_count,comments_count,timestamp',
                'limit': 25,
                'access_token': self.access_token
            }
            
            media_response = self.session.get(media_url, params=media_params, timeout=30)
            
            if media_response.status_code != 200:
                self.handle_api_error(media_response, "get_engagement_metrics")
            
            media_data = media_response.json()
            posts = media_data.get('data', [])
            
            # Calculate engagement
            total_likes = sum(post.get('like_count', 0) for post in posts)
            total_comments = sum(post.get('comments_count', 0) for post in posts)
            total_engagement = total_likes + total_comments
            
            followers = profile.get('followers_count', 1)
            posts_count = len(posts)
            
            engagement_rate = (total_engagement / (followers * posts_count) * 100) if posts_count > 0 else 0
            
            return {
                'follower_count': followers,
                'following_count': profile.get('follows_count', 0),
                'posts_count': profile.get('media_count', 0),
                'likes_count': total_likes,
                'comments_count': total_comments,
                'engagement_rate': round(engagement_rate, 2)
            }
        
        except requests.RequestException as e:
            logger.error(f"Instagram engagement metrics request failed: {e}")
            raise APIError(f"Failed to fetch Instagram engagement metrics: {e}")
    
    def refresh_access_token(self) -> Tuple[str, str, datetime]:
        """Refresh Instagram access token (long-lived tokens)"""
        try:
            url = f"{self.GRAPH_URL}/oauth/access_token"
            params = {
                'grant_type': 'ig_refresh_token',
                'access_token': self.access_token
            }
            
            response = self.session.get(url, params=params, timeout=30)
            
            if response.status_code != 200:
                self.handle_api_error(response, "refresh_access_token")
            
            data = response.json()
            new_token = data.get('access_token')
            expires_in = data.get('expires_in', 5184000)  # Default 60 days
            
            expires_at = timezone.now() + timedelta(seconds=expires_in)
            
            return new_token, "", expires_at
        
        except requests.RequestException as e:
            logger.error(f"Instagram token refresh failed: {e}")
            raise APIError(f"Failed to refresh Instagram token: {e}")


class YouTubeAPIClient(BaseSocialMediaClient):
    """YouTube Data API v3 Client"""
    
    BASE_URL = "https://www.googleapis.com/youtube/v3"
    OAUTH_URL = "https://oauth2.googleapis.com/token"
    
    def get_user_profile(self) -> Dict:
        """Get YouTube channel information"""
        try:
            url = f"{self.BASE_URL}/channels"
            params = {
                'part': 'snippet,statistics',
                'mine': 'true',
                'access_token': self.access_token
            }
            
            response = self.session.get(url, params=params, timeout=30)
            
            if response.status_code != 200:
                self.handle_api_error(response, "get_user_profile")
            
            data = response.json()
            
            if not data.get('items'):
                raise APIError("No YouTube channel found for this account")
            
            channel = data['items'][0]
            
            return {
                'id': channel['id'],
                'username': channel['snippet'].get('customUrl', ''),
                'title': channel['snippet']['title'],
                'description': channel['snippet']['description'],
                'thumbnail': channel['snippet']['thumbnails']['default']['url'],
                'subscriber_count': int(channel['statistics'].get('subscriberCount', 0)),
                'video_count': int(channel['statistics'].get('videoCount', 0)),
                'view_count': int(channel['statistics'].get('viewCount', 0))
            }
        
        except requests.RequestException as e:
            logger.error(f"YouTube API request failed: {e}")
            raise APIError(f"Failed to fetch YouTube profile: {e}")
    
    def get_follower_count(self) -> int:
        """Get YouTube subscriber count"""
        profile = self.get_user_profile()
        return profile.get('subscriber_count', 0)
    
    def get_engagement_metrics(self) -> Dict:
        """Get YouTube engagement metrics"""
        try:
            profile = self.get_user_profile()
            channel_id = profile['id']
            
            # Get recent videos
            videos_url = f"{self.BASE_URL}/search"
            videos_params = {
                'part': 'id',
                'channelId': channel_id,
                'order': 'date',
                'maxResults': 10,
                'type': 'video',
                'access_token': self.access_token
            }
            
            videos_response = self.session.get(videos_url, params=videos_params, timeout=30)
            
            if videos_response.status_code != 200:
                self.handle_api_error(videos_response, "get_engagement_metrics")
            
            videos_data = videos_response.json()
            video_ids = [item['id']['videoId'] for item in videos_data.get('items', [])]
            
            if not video_ids:
                return {
                    'follower_count': profile['subscriber_count'],
                    'following_count': 0,
                    'posts_count': profile['video_count'],
                    'likes_count': 0,
                    'comments_count': 0,
                    'views_count': profile['view_count'],
                    'engagement_rate': 0
                }
            
            # Get video statistics
            stats_url = f"{self.BASE_URL}/videos"
            stats_params = {
                'part': 'statistics',
                'id': ','.join(video_ids),
                'access_token': self.access_token
            }
            
            stats_response = self.session.get(stats_url, params=stats_params, timeout=30)
            
            if stats_response.status_code != 200:
                self.handle_api_error(stats_response, "get_video_statistics")
            
            stats_data = stats_response.json()
            
            total_likes = 0
            total_comments = 0
            total_views = 0
            
            for video in stats_data.get('items', []):
                stats = video.get('statistics', {})
                total_likes += int(stats.get('likeCount', 0))
                total_comments += int(stats.get('commentCount', 0))
                total_views += int(stats.get('viewCount', 0))
            
            # Calculate engagement rate
            subscribers = profile['subscriber_count']
            video_count = len(video_ids)
            total_engagement = total_likes + total_comments
            
            engagement_rate = (total_engagement / (subscribers * video_count) * 100) if video_count > 0 and subscribers > 0 else 0
            
            return {
                'follower_count': subscribers,
                'following_count': 0,
                'posts_count': profile['video_count'],
                'likes_count': total_likes,
                'comments_count': total_comments,
                'views_count': total_views,
                'engagement_rate': round(engagement_rate, 2)
            }
        
        except requests.RequestException as e:
            logger.error(f"YouTube engagement metrics request failed: {e}")
            raise APIError(f"Failed to fetch YouTube engagement metrics: {e}")
    
    def refresh_access_token(self) -> Tuple[str, str, datetime]:
        """Refresh YouTube/Google OAuth token"""
        try:
            if not self.refresh_token:
                raise APIError("No refresh token available")
            
            data = {
                'client_id': settings.YOUTUBE_CLIENT_ID,
                'client_secret': settings.YOUTUBE_CLIENT_SECRET,
                'refresh_token': self.refresh_token,
                'grant_type': 'refresh_token'
            }
            
            response = self.session.post(self.OAUTH_URL, data=data, timeout=30)
            
            if response.status_code != 200:
                self.handle_api_error(response, "refresh_access_token")
            
            token_data = response.json()
            new_access_token = token_data['access_token']
            expires_in = token_data.get('expires_in', 3600)
            
            expires_at = timezone.now() + timedelta(seconds=expires_in)
            
            # Refresh token stays the same for Google OAuth
            return new_access_token, self.refresh_token, expires_at
        
        except requests.RequestException as e:
            logger.error(f"YouTube token refresh failed: {e}")
            raise APIError(f"Failed to refresh YouTube token: {e}")


# API Client Factory
def get_api_client(platform: str, access_token: str, refresh_token: Optional[str] = None) -> BaseSocialMediaClient:
    """Factory function to get the appropriate API client"""
    clients = {
        'instagram': InstagramGraphAPIClient,
        'youtube': YouTubeAPIClient,
    }
    
    client_class = clients.get(platform.lower())
    if not client_class:
        raise ValueError(f"Unsupported platform: {platform}")
    
    return client_class(access_token, refresh_token)


# Custom Exceptions
class APIError(Exception):
    """Base exception for API errors"""
    pass


class UnauthorizedError(APIError):
    """Raised when access token is invalid or expired"""
    pass


class ForbiddenError(APIError):
    """Raised when insufficient permissions"""
    pass


class RateLimitError(APIError):
    """Raised when rate limit is exceeded"""
    pass
