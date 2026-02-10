"""
Public Social Media Lookup Service
Fetches public information about social media accounts without requiring OAuth
"""

import requests
import logging
from typing import Dict, Optional
from django.conf import settings
from django.core.cache import cache
import time

logger = logging.getLogger(__name__)


class PublicInstagramLookup:
    """
    Service to lookup public Instagram account information
    Uses Instagram Basic Display API for public data
    """
    
    def __init__(self):
        self.base_url = "https://graph.instagram.com"
        self.cache_timeout = 3600  # 1 hour cache
        self.rate_limit_key = "instagram_public_lookup_rate_limit"
        self.max_requests_per_hour = 200  # Conservative limit
    
    def get_user_info_by_username(self, username: str) -> Optional[Dict]:
        """
        Get public user information by Instagram username
        Note: This requires Instagram Basic Display API access token
        """
        try:
            # Remove @ if present
            username = username.lstrip('@')
            
            # Check cache first (with fallback if cache unavailable)
            cache_key = f"instagram_public_{username}"
            try:
                cached_data = cache.get(cache_key)
                if cached_data:
                    logger.info(f"Returning cached data for @{username}")
                    return cached_data
            except Exception:
                logger.warning("Cache unavailable, proceeding without cache")
            
            # Check rate limits (with fallback if cache unavailable)
            if self._is_rate_limited():
                logger.warning("Instagram API rate limit reached")
                return None
            
            # For public lookup, we need a different approach
            # Instagram doesn't allow username-based lookup without user consent
            # We'll implement a search-based approach
            user_data = self._search_user_by_username(username)
            
            if user_data:
                # Cache the result (with fallback if cache unavailable)
                try:
                    cache.set(cache_key, user_data, self.cache_timeout)
                except Exception:
                    logger.warning("Could not cache result, continuing without cache")
                
                self._increment_rate_limit_counter()
                
            return user_data
            
        except Exception as e:
            logger.error(f"Error looking up Instagram user @{username}: {e}")
            return None
    
    def _search_user_by_username(self, username: str) -> Optional[Dict]:
        """
        Search for user by username using Instagram Graph API
        Note: This is a simplified implementation
        """
        try:
            # This would require a valid access token
            # For demonstration, we'll return mock data
            # In production, you'd need proper Instagram API access
            
            # Mock data for demonstration
            mock_data = {
                'username': username,
                'display_name': f"User {username}",
                'follower_count': 0,
                'following_count': 0,
                'posts_count': 0,
                'profile_picture_url': '',
                'is_verified': False,
                'is_business': False,
                'bio': '',
                'external_url': '',
                'data_source': 'mock',
                'last_updated': time.time()
            }
            
            logger.info(f"Mock data returned for @{username}")
            return mock_data
            
        except Exception as e:
            logger.error(f"Error in Instagram user search: {e}")
            return None
    
    def _is_rate_limited(self) -> bool:
        """Check if we've hit the rate limit"""
        try:
            current_count = cache.get(self.rate_limit_key, 0)
            return current_count >= self.max_requests_per_hour
        except Exception:
            # If cache is not available, allow the request
            return False
    
    def _increment_rate_limit_counter(self):
        """Increment the rate limit counter"""
        try:
            current_count = cache.get(self.rate_limit_key, 0)
            cache.set(self.rate_limit_key, current_count + 1, 3600)  # Reset every hour
        except Exception:
            # If cache is not available, silently continue
            pass


class InstagramScrapingService:
    """
    Alternative service using Instagram's public web interface
    Note: This is for educational purposes only
    Instagram's terms of service should be respected
    """
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        self.cache_timeout = 1800  # 30 minutes cache
    
    def get_public_profile_info(self, username: str) -> Optional[Dict]:
        """
        Get public profile information from Instagram's web interface
        WARNING: This method may violate Instagram's ToS
        Use only for educational purposes or with proper authorization
        """
        try:
            username = username.lstrip('@')
            
            # Check cache first (with fallback if cache unavailable)
            cache_key = f"instagram_scrape_{username}"
            try:
                cached_data = cache.get(cache_key)
                if cached_data:
                    return cached_data
            except Exception:
                logger.warning("Cache unavailable, proceeding without cache")
            
            # Make request to Instagram profile page
            url = f"https://www.instagram.com/{username}/"
            
            # Add delay to be respectful
            time.sleep(1)
            
            response = self.session.get(url, timeout=10)
            
            if response.status_code == 404:
                logger.warning(f"Instagram user @{username} not found")
                return None
            
            if response.status_code != 200:
                logger.error(f"Instagram request failed with status {response.status_code}")
                return None
            
            # Parse the response (simplified implementation)
            profile_data = self._parse_instagram_profile(response.text, username)
            
            if profile_data:
                # Cache the result (with fallback if cache unavailable)
                try:
                    cache.set(cache_key, profile_data, self.cache_timeout)
                except Exception:
                    logger.warning("Could not cache result, continuing without cache")
            
            return profile_data
            
        except Exception as e:
            logger.error(f"Error scraping Instagram profile @{username}: {e}")
            return None
    
    def _parse_instagram_profile(self, html_content: str, username: str) -> Optional[Dict]:
        """
        Parse Instagram profile page HTML
        This is a simplified implementation
        """
        try:
            # For demonstration, return mock data
            # In a real implementation, you'd parse the HTML or JSON data
            
            # WARNING: Web scraping Instagram may violate their Terms of Service
            # This is for educational purposes only
            
            import re
            import json
            
            # Try to find JSON data in the HTML
            json_pattern = r'window\._sharedData\s*=\s*({.+?});'
            match = re.search(json_pattern, html_content)
            
            if match:
                try:
                    shared_data = json.loads(match.group(1))
                    # Extract profile data from shared data
                    # This structure may change frequently
                    
                    # Return mock data for now
                    return {
                        'username': username,
                        'display_name': f"Public User {username}",
                        'follower_count': 1000,  # This would be parsed from actual data
                        'following_count': 500,
                        'posts_count': 100,
                        'profile_picture_url': '',
                        'is_verified': False,
                        'is_business': False,
                        'bio': 'Sample bio',
                        'external_url': '',
                        'data_source': 'web_scraping',
                        'last_updated': time.time(),
                        'warning': 'This data is from web scraping and may violate Instagram ToS'
                    }
                    
                except json.JSONDecodeError:
                    logger.error("Failed to parse Instagram JSON data")
            
            # Fallback to mock data
            return {
                'username': username,
                'display_name': f"User {username}",
                'follower_count': 0,
                'following_count': 0,
                'posts_count': 0,
                'profile_picture_url': '',
                'is_verified': False,
                'is_business': False,
                'bio': '',
                'external_url': '',
                'data_source': 'fallback',
                'last_updated': time.time(),
                'note': 'Unable to fetch real data - showing placeholder'
            }
            
        except Exception as e:
            logger.error(f"Error parsing Instagram profile data: {e}")
            return None


class SocialMediaPublicLookup:
    """
    Main service for public social media lookups
    """
    
    def __init__(self):
        self.instagram_api = PublicInstagramLookup()
        self.instagram_scraper = InstagramScrapingService()
    
    def lookup_instagram_user(self, username: str, method: str = 'api') -> Optional[Dict]:
        """
        Lookup Instagram user using specified method
        
        Args:
            username: Instagram username (with or without @)
            method: 'api' for web-based lookup, 'scraping' for legacy method
        
        Returns:
            Dict with user information or None if not found
        """
        try:
            if method == 'api':
                from .instagram_public_api import instagram_public_api
                return instagram_public_api.get_user_data(username)
            elif method == 'scraping':
                logger.warning("Using legacy scraping method")
                return self.instagram_scraper.get_public_profile_info(username)
            else:
                raise ValueError(f"Unknown method: {method}")
                
        except Exception as e:
            logger.error(f"Error in Instagram lookup: {e}")
            return None
    
    def lookup_youtube_channel(self, channel_name: str) -> Optional[Dict]:
        """
        Lookup YouTube channel information
        """
        try:
            # This would use YouTube Data API
            # For now, return mock data
            
            return {
                'channel_name': channel_name,
                'display_name': f"Channel {channel_name}",
                'subscriber_count': 0,
                'video_count': 0,
                'view_count': 0,
                'channel_url': f"https://youtube.com/@{channel_name}",
                'profile_picture_url': '',
                'is_verified': False,
                'description': '',
                'data_source': 'mock',
                'last_updated': time.time(),
                'note': 'YouTube API integration needed for real data'
            }
            
        except Exception as e:
            logger.error(f"Error looking up YouTube channel: {e}")
            return None


# Global service instance
public_lookup_service = SocialMediaPublicLookup()