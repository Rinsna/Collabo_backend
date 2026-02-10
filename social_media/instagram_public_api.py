"""
Instagram Public API Service
Uses Instagram's public endpoints and official APIs to fetch user data
"""

import requests
import json
import re
import time
import logging
from typing import Dict, Optional
from django.core.cache import cache
from django.conf import settings

logger = logging.getLogger(__name__)


class InstagramPublicAPI:
    """
    Service to fetch Instagram public data using various methods
    """
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
        self.cache_timeout = 1800  # 30 minutes
        self.rate_limit_key = "instagram_public_api_rate_limit"
        self.max_requests_per_hour = 100
    
    def get_user_data(self, username: str) -> Optional[Dict]:
        """
        Get Instagram user data using the most reliable method available
        """
        username = username.lstrip('@').lower()
        
        # Check cache first (with fallback if cache unavailable)
        cache_key = f"instagram_public_data_{username}"
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
            return self._get_fallback_data(username)
        
        # Try different methods in order of preference
        methods = [
            self._fetch_via_web_profile,
            self._fetch_via_public_api,
            self._get_fallback_data
        ]
        
        for method in methods:
            try:
                data = method(username)
                if data:
                    # Cache successful result (with fallback if cache unavailable)
                    try:
                        cache.set(cache_key, data, self.cache_timeout)
                    except Exception:
                        logger.warning("Could not cache result, continuing without cache")
                    
                    self._increment_rate_limit_counter()
                    return data
            except Exception as e:
                logger.warning(f"Method {method.__name__} failed for @{username}: {e}")
                continue
        
        return None
    
    def _fetch_via_web_profile(self, username: str) -> Optional[Dict]:
        """
        Fetch data from Instagram's web profile page
        """
        try:
            url = f"https://www.instagram.com/{username}/"
            
            # Add delay to be respectful
            time.sleep(1)
            
            response = self.session.get(url, timeout=15)
            
            if response.status_code == 404:
                logger.info(f"Instagram user @{username} not found (404)")
                return None
            
            if response.status_code != 200:
                logger.error(f"Instagram request failed with status {response.status_code}")
                return None
            
            # Parse the HTML content
            return self._parse_instagram_html(response.text, username)
            
        except requests.RequestException as e:
            logger.error(f"Network error fetching Instagram profile @{username}: {e}")
            return None
        except Exception as e:
            logger.error(f"Error fetching Instagram profile @{username}: {e}")
            return None
    
    def _parse_instagram_html(self, html_content: str, username: str) -> Optional[Dict]:
        """
        Parse Instagram profile HTML to extract user data
        """
        try:
            # Method 1: Try to find JSON-LD structured data
            json_ld_pattern = r'<script type="application/ld\+json"[^>]*>(.*?)</script>'
            json_ld_matches = re.findall(json_ld_pattern, html_content, re.DOTALL)
            
            for json_ld in json_ld_matches:
                try:
                    data = json.loads(json_ld)
                    if isinstance(data, dict) and data.get('@type') == 'Person':
                        return self._extract_from_json_ld(data, username)
                except json.JSONDecodeError:
                    continue
            
            # Method 2: Try to find window._sharedData
            shared_data_pattern = r'window\._sharedData\s*=\s*({.+?});'
            shared_data_match = re.search(shared_data_pattern, html_content)
            
            if shared_data_match:
                try:
                    shared_data = json.loads(shared_data_match.group(1))
                    return self._extract_from_shared_data(shared_data, username)
                except json.JSONDecodeError:
                    pass
            
            # Method 3: Try to find meta tags
            return self._extract_from_meta_tags(html_content, username)
            
        except Exception as e:
            logger.error(f"Error parsing Instagram HTML for @{username}: {e}")
            return None
    
    def _extract_from_json_ld(self, data: Dict, username: str) -> Dict:
        """Extract data from JSON-LD structured data"""
        try:
            # Extract follower count from interactionStatistic
            follower_count = 0
            if 'interactionStatistic' in data:
                for stat in data['interactionStatistic']:
                    if stat.get('interactionType') == 'http://schema.org/FollowAction':
                        follower_count = int(stat.get('userInteractionCount', 0))
                        break
            
            return {
                'username': username,
                'display_name': data.get('name', ''),
                'follower_count': follower_count,
                'following_count': 0,  # Not available in JSON-LD
                'posts_count': 0,  # Not available in JSON-LD
                'profile_picture_url': data.get('image', ''),
                'is_verified': False,  # Not available in JSON-LD
                'is_business': False,  # Not available in JSON-LD
                'bio': data.get('description', ''),
                'external_url': data.get('url', ''),
                'data_source': 'json_ld',
                'last_updated': time.time(),
                'method': 'Instagram JSON-LD'
            }
        except Exception as e:
            logger.error(f"Error extracting from JSON-LD: {e}")
            return None
    
    def _extract_from_shared_data(self, shared_data: Dict, username: str) -> Dict:
        """Extract data from window._sharedData"""
        try:
            # Navigate through the shared data structure
            entry_data = shared_data.get('entry_data', {})
            profile_page = entry_data.get('ProfilePage', [])
            
            if not profile_page:
                return None
            
            user_data = profile_page[0].get('graphql', {}).get('user', {})
            
            if not user_data:
                return None
            
            return {
                'username': user_data.get('username', username),
                'display_name': user_data.get('full_name', ''),
                'follower_count': user_data.get('edge_followed_by', {}).get('count', 0),
                'following_count': user_data.get('edge_follow', {}).get('count', 0),
                'posts_count': user_data.get('edge_owner_to_timeline_media', {}).get('count', 0),
                'profile_picture_url': user_data.get('profile_pic_url_hd', ''),
                'is_verified': user_data.get('is_verified', False),
                'is_business': user_data.get('is_business_account', False),
                'bio': user_data.get('biography', ''),
                'external_url': user_data.get('external_url', ''),
                'data_source': 'shared_data',
                'last_updated': time.time(),
                'method': 'Instagram Shared Data'
            }
        except Exception as e:
            logger.error(f"Error extracting from shared data: {e}")
            return None
    
    def _extract_from_meta_tags(self, html_content: str, username: str) -> Dict:
        """Extract basic data from meta tags"""
        try:
            # Extract title and description from meta tags
            title_match = re.search(r'<title[^>]*>([^<]+)</title>', html_content, re.IGNORECASE)
            description_match = re.search(r'<meta[^>]*name=["\']description["\'][^>]*content=["\']([^"\']+)["\']', html_content, re.IGNORECASE)
            
            title = title_match.group(1) if title_match else ''
            description = description_match.group(1) if description_match else ''
            
            # Try to extract follower count from title or description
            follower_count = 0
            follower_patterns = [
                r'(\d+(?:,\d+)*)\s*[Ff]ollowers',
                r'(\d+(?:\.\d+)?[KMB]?)\s*[Ff]ollowers'
            ]
            
            for pattern in follower_patterns:
                match = re.search(pattern, title + ' ' + description)
                if match:
                    follower_str = match.group(1).replace(',', '')
                    if 'K' in follower_str:
                        follower_count = int(float(follower_str.replace('K', '')) * 1000)
                    elif 'M' in follower_str:
                        follower_count = int(float(follower_str.replace('M', '')) * 1000000)
                    elif 'B' in follower_str:
                        follower_count = int(float(follower_str.replace('B', '')) * 1000000000)
                    else:
                        follower_count = int(follower_str)
                    break
            
            return {
                'username': username,
                'display_name': title.split('(')[0].strip() if '(' in title else '',
                'follower_count': follower_count,
                'following_count': 0,
                'posts_count': 0,
                'profile_picture_url': '',
                'is_verified': False,
                'is_business': False,
                'bio': description,
                'external_url': '',
                'data_source': 'meta_tags',
                'last_updated': time.time(),
                'method': 'Instagram Meta Tags'
            }
        except Exception as e:
            logger.error(f"Error extracting from meta tags: {e}")
            return None
    
    def _fetch_via_public_api(self, username: str) -> Optional[Dict]:
        """
        Fetch data using Instagram's public API endpoints
        Note: This requires proper API access tokens
        """
        try:
            # This would require Instagram Basic Display API or Graph API access
            # For now, return None to fall back to other methods
            return None
        except Exception as e:
            logger.error(f"Public API fetch failed for @{username}: {e}")
            return None
    
    def _get_fallback_data(self, username: str) -> Dict:
        """
        Return fallback data when all other methods fail
        """
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
            'method': 'Fallback Data',
            'note': 'Unable to fetch real data - showing placeholder information'
        }
    
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
    
    def get_rate_limit_status(self) -> Dict:
        """Get current rate limit status"""
        try:
            current_count = cache.get(self.rate_limit_key, 0)
            return {
                'requests_made': current_count,
                'requests_remaining': max(0, self.max_requests_per_hour - current_count),
                'limit': self.max_requests_per_hour,
                'reset_time': 3600  # 1 hour in seconds
            }
        except Exception:
            # If cache is not available, return default values
            return {
                'requests_made': 0,
                'requests_remaining': self.max_requests_per_hour,
                'limit': self.max_requests_per_hour,
                'reset_time': 3600,
                'note': 'Cache unavailable - rate limiting disabled'
            }


# Global service instance
instagram_public_api = InstagramPublicAPI()