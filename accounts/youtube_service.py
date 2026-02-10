import requests
import re
import json
from django.conf import settings

class YouTubeService:
    """Service to fetch YouTube video statistics"""
    
    API_KEY = getattr(settings, 'YOUTUBE_API_KEY', None)
    BASE_URL = 'https://www.googleapis.com/youtube/v3/videos'
    
    @staticmethod
    def extract_video_id(url):
        """Extract video ID from various YouTube URL formats"""
        if not url or url == '#':
            return None
        
        # Standard watch URL: https://www.youtube.com/watch?v=VIDEO_ID
        if 'youtube.com/watch?v=' in url:
            match = re.search(r'v=([a-zA-Z0-9_-]+)', url)
            if match:
                return match.group(1)
        
        # Short URL: https://youtu.be/VIDEO_ID
        elif 'youtu.be/' in url:
            match = re.search(r'youtu\.be/([a-zA-Z0-9_-]+)', url)
            if match:
                return match.group(1)
        
        # Embed URL: https://www.youtube.com/embed/VIDEO_ID
        elif 'youtube.com/embed/' in url:
            match = re.search(r'embed/([a-zA-Z0-9_-]+)', url)
            if match:
                return match.group(1)
        
        return None
    
    @classmethod
    def get_video_stats(cls, video_url):
        """
        Fetch video statistics from YouTube
        Returns: dict with 'views' and 'likes' or None if failed
        """
        video_id = cls.extract_video_id(video_url)
        
        if not video_id:
            print(f"Could not extract video ID from: {video_url}")
            return None
        
        # If API key is available, use official API
        if cls.API_KEY:
            return cls.get_video_stats_api(video_id)
        
        # Otherwise use fallback method
        return cls.get_video_stats_fallback(video_id)
    
    @classmethod
    def get_video_stats_api(cls, video_id):
        """Fetch stats using YouTube Data API v3"""
        try:
            params = {
                'part': 'statistics',
                'id': video_id,
                'key': cls.API_KEY
            }
            
            response = requests.get(cls.BASE_URL, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                if 'items' in data and len(data['items']) > 0:
                    stats = data['items'][0].get('statistics', {})
                    
                    return {
                        'views': int(stats.get('viewCount', 0)),
                        'likes': int(stats.get('likeCount', 0))
                    }
            
            print(f"API request failed: {response.status_code}")
            return None
            
        except Exception as e:
            print(f"Error fetching YouTube stats via API: {e}")
            return None
    
    @staticmethod
    def get_video_stats_fallback(video_id):
        """
        Fallback method using YouTube's internal API (no auth required)
        """
        try:
            url = f'https://www.youtube.com/watch?v={video_id}'
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept-Language': 'en-US,en;q=0.9',
            }
            
            response = requests.get(url, headers=headers, timeout=15)
            
            if response.status_code == 200:
                content = response.text
                
                # Try multiple patterns to extract view count
                view_patterns = [
                    r'"viewCount":"(\d+)"',
                    r'"views":\{"simpleText":"([\d,]+)',
                    r'viewCount":"(\d+)"',
                ]
                
                views = 0
                for pattern in view_patterns:
                    match = re.search(pattern, content)
                    if match:
                        views = int(match.group(1).replace(',', ''))
                        break
                
                # Try multiple patterns for likes
                like_patterns = [
                    r'"label":"([\d,]+) likes"',
                    r'accessibilityText":"([\d,]+) likes"',
                    r'"likeCount":"(\d+)"',
                ]
                
                likes = 0
                for pattern in like_patterns:
                    match = re.search(pattern, content)
                    if match:
                        likes = int(match.group(1).replace(',', ''))
                        break
                
                if views > 0:
                    return {
                        'views': views,
                        'likes': likes
                    }
            
            print(f"Failed to fetch YouTube page: {response.status_code}")
            return None
            
        except Exception as e:
            print(f"Error in YouTube fallback: {e}")
            return None


class InstagramService:
    """Service to fetch Instagram reel/post statistics"""
    
    @staticmethod
    def extract_shortcode(url):
        """Extract shortcode from Instagram URL"""
        if not url or url == '#':
            return None
        
        # Reel URL: https://www.instagram.com/reel/SHORTCODE/
        if 'instagram.com/reel/' in url:
            match = re.search(r'/reel/([A-Za-z0-9_-]+)', url)
            if match:
                return match.group(1)
        
        # Post URL: https://www.instagram.com/p/SHORTCODE/
        elif 'instagram.com/p/' in url:
            match = re.search(r'/p/([A-Za-z0-9_-]+)', url)
            if match:
                return match.group(1)
        
        return None
    
    @classmethod
    def get_post_stats(cls, post_url):
        """
        Fetch Instagram post/reel statistics
        Returns: dict with 'views' and 'likes' or None if failed
        """
        shortcode = cls.extract_shortcode(post_url)
        
        if not shortcode:
            print(f"Could not extract shortcode from: {post_url}")
            return None
        
        try:
            # Use Instagram's oEmbed endpoint (public, no auth required)
            oembed_url = f'https://www.instagram.com/p/{shortcode}/embed/captioned/'
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.9',
            }
            
            response = requests.get(oembed_url, headers=headers, timeout=15)
            
            if response.status_code == 200:
                content = response.text
                
                # Try to extract view count (for reels)
                view_patterns = [
                    r'"video_view_count":(\d+)',
                    r'video_view_count&quot;:(\d+)',
                    r'"view_count":(\d+)',
                ]
                
                views = 0
                for pattern in view_patterns:
                    match = re.search(pattern, content)
                    if match:
                        views = int(match.group(1))
                        break
                
                # Try to extract like count
                like_patterns = [
                    r'"edge_media_preview_like":\{"count":(\d+)',
                    r'"edge_liked_by":\{"count":(\d+)',
                    r'edge_liked_by&quot;:\{&quot;count&quot;:(\d+)',
                ]
                
                likes = 0
                for pattern in like_patterns:
                    match = re.search(pattern, content)
                    if match:
                        likes = int(match.group(1))
                        break
                
                # If we got at least one stat, return it
                if views > 0 or likes > 0:
                    return {
                        'views': views,
                        'likes': likes
                    }
                
                # Try alternative method - fetch the actual post page
                return cls.get_post_stats_alternative(shortcode)
            
            print(f"Failed to fetch Instagram embed: {response.status_code}")
            return cls.get_post_stats_alternative(shortcode)
            
        except Exception as e:
            print(f"Error fetching Instagram stats: {e}")
            return cls.get_post_stats_alternative(shortcode)
    
    @staticmethod
    def get_post_stats_alternative(shortcode):
        """Alternative method to fetch Instagram stats"""
        try:
            url = f'https://www.instagram.com/p/{shortcode}/'
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml',
                'Accept-Language': 'en-US,en;q=0.9',
            }
            
            response = requests.get(url, headers=headers, timeout=15)
            
            if response.status_code == 200:
                content = response.text
                
                # Look for JSON data in the page
                match = re.search(r'window\._sharedData = ({.*?});</script>', content)
                if match:
                    try:
                        data = json.loads(match.group(1))
                        media = data.get('entry_data', {}).get('PostPage', [{}])[0].get('graphql', {}).get('shortcode_media', {})
                        
                        views = media.get('video_view_count', 0)
                        likes = media.get('edge_media_preview_like', {}).get('count', 0)
                        
                        if views > 0 or likes > 0:
                            return {
                                'views': views,
                                'likes': likes
                            }
                    except:
                        pass
                
                # Try regex patterns as last resort
                view_match = re.search(r'"video_view_count":(\d+)', content)
                like_match = re.search(r'"edge_liked_by":\{"count":(\d+)', content)
                
                if view_match or like_match:
                    return {
                        'views': int(view_match.group(1)) if view_match else 0,
                        'likes': int(like_match.group(1)) if like_match else 0
                    }
            
            return None
            
        except Exception as e:
            print(f"Error in Instagram alternative method: {e}")
            return None


class VideoStatsService:
    """Unified service to fetch stats from any platform"""
    
    @staticmethod
    def get_stats(url):
        """
        Fetch statistics from any supported platform
        Returns: dict with 'views' and 'likes' or None if failed
        """
        if not url or url == '#':
            return None
        
        # Detect platform and use appropriate service
        if 'youtube.com' in url or 'youtu.be' in url:
            return YouTubeService.get_video_stats(url)
        elif 'instagram.com' in url:
            return InstagramService.get_post_stats(url)
        else:
            print(f"Unsupported platform: {url}")
            return None
    
    @classmethod
    def update_profile_video_stats(cls, profile):
        """
        Update video statistics for an influencer profile
        """
        updated = False
        
        # Update latest product review stats
        if profile.latest_product_review_link and profile.latest_product_review_link != '#':
            print(f"Fetching stats for latest review: {profile.latest_product_review_link}")
            stats = cls.get_stats(profile.latest_product_review_link)
            if stats:
                profile.latest_product_review_views = stats['views']
                profile.latest_product_review_likes = stats['likes']
                print(f"  Views: {stats['views']}, Likes: {stats['likes']}")
                updated = True
            else:
                print("  Failed to fetch stats")
        
        # Update most viewed content stats
        if profile.most_viewed_content_link and profile.most_viewed_content_link != '#':
            print(f"Fetching stats for most viewed: {profile.most_viewed_content_link}")
            stats = cls.get_stats(profile.most_viewed_content_link)
            if stats:
                profile.most_viewed_content_views = stats['views']
                profile.most_viewed_content_likes = stats['likes']
                print(f"  Views: {stats['views']}, Likes: {stats['likes']}")
                updated = True
            else:
                print("  Failed to fetch stats")
        
        if updated:
            profile.save()
            print("Profile saved successfully")
        
        return updated