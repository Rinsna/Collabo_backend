# Social Media Integration System

## Overview

This system provides automatic follower count updates for influencers using official social media APIs. It's designed to be production-safe, secure, and scalable.

## Features

- **Official API Integration**: Uses Instagram Graph API and YouTube Data API v3
- **Secure Token Storage**: Encrypted access and refresh tokens using Fernet encryption
- **Background Tasks**: Celery-based async processing for scalability
- **Automatic Refresh**: Token refresh and scheduled sync jobs
- **Rate Limiting**: Built-in rate limiting and error handling
- **Webhook Support**: Real-time updates via platform webhooks
- **Historical Data**: Track follower count changes over time
- **Admin Dashboard**: Comprehensive monitoring and management

## Architecture

### Models

1. **SocialMediaAccount**: Stores encrypted OAuth tokens and account metadata
2. **FollowerHistory**: Historical follower count and engagement data
3. **SyncJob**: Track sync operations and their status
4. **WebhookEvent**: Store and process webhook events

### Services

1. **API Clients**: Platform-specific API communication
2. **Sync Service**: Core synchronization logic
3. **Celery Tasks**: Background job processing
4. **Management Commands**: CLI tools for administration

## Setup Instructions

### 1. Install Dependencies

```bash
pip install cryptography requests celery redis django-redis
```

### 2. Environment Variables

Add these to your `.env` file:

```env
# Instagram API (Business/Creator accounts)
INSTAGRAM_CLIENT_ID=your_instagram_client_id
INSTAGRAM_CLIENT_SECRET=your_instagram_client_secret
INSTAGRAM_REDIRECT_URI=http://localhost:3000/auth/instagram/callback

# YouTube API
YOUTUBE_CLIENT_ID=your_youtube_client_id
YOUTUBE_CLIENT_SECRET=your_youtube_client_secret
YOUTUBE_REDIRECT_URI=http://localhost:3000/auth/youtube/callback

# Encryption key for token storage
SOCIAL_MEDIA_ENCRYPTION_KEY=your_fernet_encryption_key

# Redis for Celery and caching
REDIS_URL=redis://localhost:6379
```

### 3. Generate Encryption Key

```python
from cryptography.fernet import Fernet
key = Fernet.generate_key()
print(key.decode())  # Use this as SOCIAL_MEDIA_ENCRYPTION_KEY
```

### 4. Run Migrations

```bash
python manage.py migrate
```

### 5. Start Celery Workers

```bash
# In separate terminals:
celery -A influencer_platform worker --loglevel=info
celery -A influencer_platform beat --loglevel=info
```

## API Endpoints

### Social Media Accounts

- `GET /api/social-media/accounts/` - List user's connected accounts
- `POST /api/social-media/accounts/` - Create new account connection
- `GET /api/social-media/accounts/{id}/` - Get account details
- `PUT /api/social-media/accounts/{id}/` - Update account
- `DELETE /api/social-media/accounts/{id}/disconnect/` - Disconnect account
- `POST /api/social-media/accounts/{id}/sync/` - Trigger manual sync
- `GET /api/social-media/accounts/{id}/history/` - Get follower history

### OAuth Connection

- `POST /api/social-media/connect/` - Complete OAuth flow

### Sync Operations

- `POST /api/social-media/sync/user/` - Sync all user accounts
- `GET /api/social-media/sync/status/{task_id}/` - Get sync status

### Statistics

- `GET /api/social-media/stats/follower/` - Aggregated follower stats
- `GET /api/social-media/stats/sync/` - Sync history
- `GET /api/social-media/stats/admin/` - Admin statistics

### Webhooks

- `POST /api/social-media/webhooks/{platform}/` - Receive platform webhooks

## OAuth Flow

### Instagram (Business/Creator)

1. Redirect user to Instagram OAuth:
```
https://api.instagram.com/oauth/authorize?
  client_id={CLIENT_ID}&
  redirect_uri={REDIRECT_URI}&
  scope=user_profile,user_media&
  response_type=code
```

2. Handle callback and exchange code:
```javascript
// Frontend callback handler
const code = new URLSearchParams(window.location.search).get('code');
const response = await fetch('/api/social-media/connect/', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    platform: 'instagram',
    auth_code: code
  })
});
```

### YouTube

1. Redirect user to Google OAuth:
```
https://accounts.google.com/oauth2/auth?
  client_id={CLIENT_ID}&
  redirect_uri={REDIRECT_URI}&
  scope=https://www.googleapis.com/auth/youtube.readonly&
  response_type=code&
  access_type=offline
```

2. Handle callback similarly to Instagram

## Management Commands

### Sync Accounts

```bash
# Sync all accounts
python manage.py sync_social_accounts --all

# Sync specific user
python manage.py sync_social_accounts --user 123

# Sync specific platform
python manage.py sync_social_accounts --platform instagram

# Sync specific account
python manage.py sync_social_accounts --account 456

# Dry run (preview only)
python manage.py sync_social_accounts --all --dry-run
```

### Cleanup Old Data

```bash
# Clean up data older than 90 days
python manage.py cleanup_social_data

# Clean up data older than 30 days
python manage.py cleanup_social_data --days 30

# Dry run
python manage.py cleanup_social_data --dry-run
```

## Scheduled Tasks

The system includes these automatic tasks:

- **Hourly**: Sync all active accounts
- **Every 6 hours**: Refresh expiring tokens
- **Daily**: Clean up old data and generate reports

## Security Features

1. **Encrypted Token Storage**: All access tokens encrypted with Fernet
2. **Secure Key Management**: Encryption keys stored in environment variables
3. **Rate Limiting**: Automatic rate limit handling and backoff
4. **Error Handling**: Comprehensive error tracking and recovery
5. **Webhook Verification**: Signature verification for webhooks
6. **Permission Checks**: User-based access control

## Monitoring

### Admin Dashboard

Access sync statistics and account status:

```python
from social_media.sync_service import sync_service

# Get sync statistics
stats = sync_service.get_sync_statistics(days=7)

# Get account sync history
history = sync_service.get_account_sync_history(account_id=123)
```

### Logging

All operations are logged with appropriate levels:

```python
import logging
logger = logging.getLogger('social_media')
```

## Error Handling

The system handles various error scenarios:

1. **Token Expiration**: Automatic token refresh
2. **Rate Limits**: Exponential backoff and retry
3. **API Errors**: Graceful degradation and error tracking
4. **Network Issues**: Retry mechanisms with timeouts
5. **Account Deauthorization**: Status updates and notifications

## Production Deployment

### Redis Configuration

```python
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
    }
}
```

### Celery Configuration

```python
CELERY_BROKER_URL = 'redis://localhost:6379'
CELERY_RESULT_BACKEND = 'redis://localhost:6379'
```

### Environment Setup

1. Set up Redis server
2. Configure environment variables
3. Set up SSL certificates for webhooks
4. Configure monitoring and alerting

## API Rate Limits

### Instagram Graph API
- 200 calls per hour per user
- Automatic rate limit handling

### YouTube Data API v3
- 10,000 units per day per project
- Different operations consume different units

## Troubleshooting

### Common Issues

1. **Token Expired**: Check token refresh mechanism
2. **Rate Limited**: Wait for rate limit reset
3. **Invalid Credentials**: Verify API keys and secrets
4. **Webhook Failures**: Check signature verification
5. **Sync Failures**: Review error logs and retry

### Debug Commands

```bash
# Check account status
python manage.py shell
>>> from social_media.models import SocialMediaAccount
>>> accounts = SocialMediaAccount.objects.filter(status='error')
>>> for account in accounts:
...     print(f"{account}: {account.last_error}")

# Test API connection
>>> from social_media.api_clients import get_api_client
>>> client = get_api_client('instagram', 'your_token')
>>> profile = client.get_user_profile()
```

## Migration from Legacy System

The new system maintains backward compatibility with existing endpoints:

- `/api/social-media/update-followers/` - Legacy endpoint
- `/api/social-media/update-followers-sync/` - Legacy sync endpoint
- `/api/social-media/follower-stats/` - Legacy stats endpoint

## Future Enhancements

1. **Additional Platforms**: TikTok, Twitter, Facebook
2. **Advanced Analytics**: Engagement trends, growth predictions
3. **Real-time Notifications**: WebSocket updates
4. **Bulk Operations**: Batch account management
5. **API Versioning**: Support for multiple API versions

## Support

For issues and questions:

1. Check the logs in `logs/social_media.log`
2. Review error messages in admin dashboard
3. Use management commands for debugging
4. Monitor Celery task status

## License

This social media integration system is part of the influencer collaboration platform.