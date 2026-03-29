import requests
import instaloader
from googleapiclient.discovery import build
from django.conf import settings
import logging
import re
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)

class SocialMediaService:
    """Service class for fetching social media data"""
    
    @staticmethod
    def get_instagram_followers(username: str) -> Optional[int]:
        """
        Get Instagram follower count using instaloader
        Note: This is a basic implementation. For production, consider using official Instagram API
        """
        try:
            # Remove @ symbol if present
            username = username.lstrip('@')
            
            # Create instaloader instance
            loader = instaloader.Instaloader()
            
            # Get profile
            profile = instaloader.Profile.from_username(loader.context, username)
            
            return profile.followers
            
        except Exception as e:
            logger.error(f"Error fetching Instagram followers for {username}: {str(e)}")
            return None
    
    @staticmethod
    def get_youtube_subscribers(channel_identifier: str) -> Optional[int]:
        """
        Get YouTube subscriber count using YouTube Data API v3
        channel_identifier can be channel URL, channel ID, or channel name
        """
        try:
            if not settings.YOUTUBE_API_KEY:
                logger.warning("YouTube API key not configured")
                return None
            
            youtube = build('youtube', 'v3', developerKey=settings.YOUTUBE_API_KEY)
            
            # Extract channel ID from different formats
            channel_id = SocialMediaService._extract_youtube_channel_id(channel_identifier)
            
            if not channel_id:
                # Try to search by channel name
                search_response = youtube.search().list(
                    q=channel_identifier,
                    type='channel',
                    part='id',
                    maxResults=1
                ).execute()
                
                if search_response['items']:
                    channel_id = search_response['items'][0]['id']['channelId']
                else:
                    logger.error(f"Could not find YouTube channel: {channel_identifier}")
                    return None
            
            # Get channel statistics
            channels_response = youtube.channels().list(
                part='statistics',
                id=channel_id
            ).execute()
            
            if channels_response['items']:
                subscriber_count = channels_response['items'][0]['statistics'].get('subscriberCount')
                if subscriber_count:
                    return int(subscriber_count)
            
            return None
            
        except Exception as e:
            logger.error(f"Error fetching YouTube subscribers for {channel_identifier}: {str(e)}")
            return None
    
    @staticmethod
    def _extract_youtube_channel_id(url_or_id: str) -> Optional[str]:
        """Extract YouTube channel ID from various URL formats"""
        # If it's already a channel ID (starts with UC and is 24 characters)
        if url_or_id.startswith('UC') and len(url_or_id) == 24:
            return url_or_id
        
        # Extract from various YouTube URL formats
        patterns = [
            r'youtube\.com/channel/([a-zA-Z0-9_-]+)',
            r'youtube\.com/c/([a-zA-Z0-9_-]+)',
            r'youtube\.com/user/([a-zA-Z0-9_-]+)',
            r'youtube\.com/@([a-zA-Z0-9_-]+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url_or_id)
            if match:
                return match.group(1)
        
        return None
    
    @staticmethod
    def update_follower_counts(influencer_profile) -> Dict[str, Any]:
        """
        Update follower counts for an influencer profile
        Returns a dictionary with update results
        """
        results = {
            'instagram_updated': False,
            'youtube_updated': False,
            'instagram_followers': None,
            'youtube_subscribers': None,
            'errors': []
        }
        
        # Update Instagram followers
        if influencer_profile.instagram_handle:
            try:
                followers = SocialMediaService.get_instagram_followers(
                    influencer_profile.instagram_handle
                )
                if followers is not None:
                    # For Instagram, we'll store it in followers_count if it's the primary platform
                    # or create a separate field for Instagram-specific count
                    if 'instagram' in influencer_profile.preferred_platforms:
                        old_count = influencer_profile.followers_count
                        influencer_profile.followers_count = followers
                        results['instagram_followers'] = followers
                        results['instagram_updated'] = True
                        logger.info(f"Updated Instagram followers for {influencer_profile.user.username}: {old_count} -> {followers}")
                else:
                    results['errors'].append("Could not fetch Instagram followers")
            except Exception as e:
                results['errors'].append(f"Instagram error: {str(e)}")
        
        # Update YouTube subscribers
        if influencer_profile.youtube_channel:
            try:
                subscribers = SocialMediaService.get_youtube_subscribers(
                    influencer_profile.youtube_channel
                )
                if subscribers is not None:
                    # If YouTube is the primary platform or only platform, update main followers_count
                    if 'youtube' in influencer_profile.preferred_platforms:
                        if 'instagram' not in influencer_profile.preferred_platforms:
                            # YouTube only
                            influencer_profile.followers_count = subscribers
                        else:
                            # Both platforms - use the higher count or combine logic
                            influencer_profile.followers_count = max(
                                influencer_profile.followers_count or 0, 
                                subscribers
                            )
                    results['youtube_subscribers'] = subscribers
                    results['youtube_updated'] = True
                    logger.info(f"Updated YouTube subscribers for {influencer_profile.user.username}: {subscribers}")
                else:
                    results['errors'].append("Could not fetch YouTube subscribers")
            except Exception as e:
                results['errors'].append(f"YouTube error: {str(e)}")
        
        # Save the profile if any updates were made
        if results['instagram_updated'] or results['youtube_updated']:
            influencer_profile.save()
        
        return results