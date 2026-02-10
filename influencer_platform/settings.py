import os
from pathlib import Path
from decouple import config
from datetime import timedelta
import dj_database_url

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = config('SECRET_KEY', default='django-insecure-change-me-in-production')

DEBUG = config('DEBUG', default=True, cast=bool)

ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='localhost,127.0.0.1,0.0.0.0').split(',')

DJANGO_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

THIRD_PARTY_APPS = [
    'rest_framework',
    'rest_framework_simplejwt',
    'corsheaders',
]

LOCAL_APPS = [
    'accounts',
    'collaborations',
    'payments',
    'social_media',
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'influencer_platform.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
            'debug': DEBUG,
        },
    },
]

WSGI_APPLICATION = 'influencer_platform.wsgi.application'

# Database Configuration
# Use PostgreSQL in production (Render), SQLite in development
DATABASE_URL = config('DATABASE_URL', default=None)

if DATABASE_URL:
    # Production: Use PostgreSQL from DATABASE_URL
    DATABASES = {
        'default': dj_database_url.parse(DATABASE_URL, conn_max_age=600)
    }
else:
    # Development: Use SQLite
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

# Ensure UTF-8 encoding for all text
DEFAULT_CHARSET = 'utf-8'
FILE_CHARSET = 'utf-8'

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# UTF-8 encoding settings
DEFAULT_CHARSET = 'utf-8'
FILE_CHARSET = 'utf-8'

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Whitenoise configuration for serving static files
STORAGES = {
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Data upload settings - Allow larger file uploads for base64 images
DATA_UPLOAD_MAX_MEMORY_SIZE = 10485760  # 10MB
FILE_UPLOAD_MAX_MEMORY_SIZE = 10485760  # 10MB

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Django 5.1 compatibility
USE_TZ = True

# Custom User Model
AUTH_USER_MODEL = 'accounts.User'

# REST Framework Configuration
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_FILTER_BACKENDS': [
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20
}

# JWT Configuration
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
}

# CORS Configuration
CORS_ALLOWED_ORIGINS = config(
    'CORS_ALLOWED_ORIGINS',
    default='http://localhost:3000,http://127.0.0.1:3000'
).split(',')

CORS_ALLOW_CREDENTIALS = True

# Stripe Configuration
STRIPE_PUBLISHABLE_KEY = config('STRIPE_PUBLISHABLE_KEY', default='')
STRIPE_SECRET_KEY = config('STRIPE_SECRET_KEY', default='')

# Celery Configuration
CELERY_BROKER_URL = config('REDIS_URL', default='redis://localhost:6379')
CELERY_RESULT_BACKEND = config('REDIS_URL', default='redis://localhost:6379')
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = TIME_ZONE

# Social Media API Configuration
INSTAGRAM_CLIENT_ID = config('INSTAGRAM_CLIENT_ID', default='')
INSTAGRAM_CLIENT_SECRET = config('INSTAGRAM_CLIENT_SECRET', default='')
INSTAGRAM_REDIRECT_URI = config('INSTAGRAM_REDIRECT_URI', default='http://localhost:3000/auth/instagram/callback')

YOUTUBE_CLIENT_ID = config('YOUTUBE_CLIENT_ID', default='')
YOUTUBE_CLIENT_SECRET = config('YOUTUBE_CLIENT_SECRET', default='')
YOUTUBE_REDIRECT_URI = config('YOUTUBE_REDIRECT_URI', default='http://localhost:3000/auth/youtube/callback')

# Social Media Encryption Key (generate with: from cryptography.fernet import Fernet; Fernet.generate_key())
SOCIAL_MEDIA_ENCRYPTION_KEY = config('SOCIAL_MEDIA_ENCRYPTION_KEY', default='')

# Legacy API keys for backward compatibility
INSTAGRAM_API_KEY = config('INSTAGRAM_API_KEY', default='')
YOUTUBE_API_KEY = config('YOUTUBE_API_KEY', default='')

# Follower update settings
FOLLOWER_UPDATE_INTERVAL = 3600  # Update every hour (in seconds)

# Celery Beat Schedule for periodic tasks
CELERY_BEAT_SCHEDULE = {
    # Sync all social accounts every hour
    'sync-all-social-accounts': {
        'task': 'social_media.tasks.sync_all_social_accounts',
        'schedule': 3600.0,  # Every hour
    },
    
    # Refresh expired tokens every 6 hours
    'refresh-expired-tokens': {
        'task': 'social_media.tasks.refresh_expired_tokens',
        'schedule': 21600.0,  # Every 6 hours
    },
    
    # Clean up old data daily at 2 AM
    'cleanup-old-sync-data': {
        'task': 'social_media.tasks.cleanup_old_sync_data',
        'schedule': 86400.0,  # Daily
    },
    
    # Generate sync report daily at 8 AM
    'generate-sync-report': {
        'task': 'social_media.tasks.generate_sync_report',
        'schedule': 86400.0,  # Daily
    },
}

# Cache configuration for rate limiting
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'unique-snowflake',
    }
}

# Use Redis cache if REDIS_URL is provided
REDIS_URL = config('REDIS_URL', default=None)
if REDIS_URL:
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.redis.RedisCache',
            'LOCATION': REDIS_URL,
        }
    }

# Logging configuration
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
    },
    'loggers': {
        'social_media': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}