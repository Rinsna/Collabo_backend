# Collabo Backend - Influencer Marketing Platform API

Django REST API backend for the Collabo influencer marketing platform.

## 🚀 Features

### Core Functionality
- **User Authentication** - JWT-based auth with role-based access
- **Profile Management** - Influencer and Company profiles
- **Campaign System** - Create, manage, and track campaigns
- **Collaboration Workflow** - Request, accept, reject collaborations
- **Payment Tracking** - Monitor budgets and earnings
- **Social Media Integration** - Auto-connect Instagram/YouTube accounts
- **Real-time Analytics** - Follower tracking and engagement metrics
- **Video Stats** - Automatic YouTube/Instagram video statistics

### Auto-Connect Social Media
- Users add Instagram/YouTube handles in profile
- System automatically creates `SocialMediaAccount` entries
- No OAuth setup required for basic functionality
- Analytics work immediately with profile data

### API Endpoints
- `/api/auth/` - Authentication (register, login, profile)
- `/api/campaigns/` - Campaign management
- `/api/collaborations/` - Collaboration requests
- `/api/payments/` - Payment tracking
- `/api/social-media/` - Social media accounts and analytics
- `/api/influencers/` - Influencer discovery

## 📦 Tech Stack

- **Django** 6.0.2 - Web framework
- **Django REST Framework** 3.15.2 - API framework
- **PostgreSQL** - Primary database
- **SQLite** - Development database (default)
- **Celery** - Async task processing
- **Redis** - Message broker for Celery
- **JWT** - Token-based authentication
- **Pillow** - Image processing
- **Cryptography** - Token encryption

## 🛠️ Installation

### Prerequisites
- Python 3.8+
- PostgreSQL (optional, SQLite works for development)
- Redis (optional, for Celery tasks)

### Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/Rinsna/Collabo_backend.git
   cd Collabo_backend
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   
   # Windows
   venv\Scripts\activate
   
   # Linux/Mac
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment**
   ```bash
   # Copy example env file
   cp .env.example .env
   
   # Edit .env with your settings
   # At minimum, set SECRET_KEY
   ```

5. **Run migrations**
   ```bash
   python manage.py migrate
   ```

6. **Create superuser**
   ```bash
   python manage.py createsuperuser
   ```

7. **Run development server**
   ```bash
   python manage.py runserver
   ```

   API will be available at http://localhost:8000

## 📁 Project Structure

```
backend/
├── accounts/              # User authentication and profiles
│   ├── models.py         # User, InfluencerProfile, CompanyProfile
│   ├── views.py          # Auth endpoints, profile management
│   ├── serializers.py    # API serializers
│   └── migrations/       # Database migrations
├── campaigns/            # Campaign management (if exists)
├── collaborations/       # Collaboration workflow
│   ├── models.py        # Campaign, CollaborationRequest
│   ├── views.py         # Campaign CRUD, collaboration endpoints
│   └── signals.py       # Payment tracking signals
├── payments/            # Payment tracking
│   ├── models.py       # Payment records
│   └── views.py        # Payment endpoints
├── social_media/        # Social media integration
│   ├── models.py       # SocialMediaAccount, FollowerHistory
│   ├── views.py        # Account connection endpoints
│   ├── analytics_views.py  # Analytics API
│   ├── tasks.py        # Celery tasks for syncing
│   └── signals.py      # Auto-create accounts on profile save
├── influencer_platform/ # Project settings
│   ├── settings.py     # Django settings
│   ├── urls.py         # URL routing
│   └── celery.py       # Celery configuration
├── manage.py           # Django management script
├── requirements.txt    # Python dependencies
├── .env.example       # Environment template
└── .gitignore         # Git ignore rules
```

## 🔧 Configuration

### Environment Variables

Create `.env` file from `.env.example`:

```env
# Required
SECRET_KEY=your-secret-key-here
DEBUG=True

# Database (SQLite by default, PostgreSQL for production)
DB_NAME=collabo_db
DB_USER=postgres
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=5432

# Optional: Social Media APIs
INSTAGRAM_API_KEY=your_key
YOUTUBE_API_KEY=your_key
```

### Database Setup

**Development (SQLite)**:
- Default configuration
- No additional setup needed
- Database file: `db.sqlite3`

**Production (PostgreSQL)**:
```bash
# Install PostgreSQL
# Create database
createdb collabo_db

# Update .env with PostgreSQL credentials
# Run migrations
python manage.py migrate
```

### Celery Setup (Optional)

For async tasks like social media syncing:

```bash
# Install Redis
# Windows: Download from https://github.com/microsoftarchive/redis/releases
# Linux: sudo apt-get install redis-server
# Mac: brew install redis

# Start Redis
redis-server

# Start Celery worker (in separate terminal)
celery -A influencer_platform worker -l info

# Start Celery beat (for scheduled tasks)
celery -A influencer_platform beat -l info
```

## 🔑 API Authentication

### Register
```bash
POST /api/auth/register/
{
  "email": "user@example.com",
  "username": "username",
  "password": "password123",
  "password_confirm": "password123",
  "user_type": "influencer",  # or "company"
  "phone": "+1234567890"
}
```

### Login
```bash
POST /api/auth/login/
{
  "email": "user@example.com",
  "password": "password123"
}

Response:
{
  "access": "jwt_access_token",
  "refresh": "jwt_refresh_token",
  "user": { ... }
}
```

### Use Token
```bash
# Add to request headers
Authorization: Bearer <access_token>
```

## 📊 Key Features Implementation

### Auto-Connect Social Media

When users save their profile with Instagram/YouTube handles:

```python
# In accounts/views.py - InfluencerProfileView
def _auto_create_social_accounts(self, request):
    # Automatically creates SocialMediaAccount entries
    # No OAuth required
    # Analytics work immediately
```

**How it works:**
1. User updates profile with `instagram_handle` or `youtube_channel`
2. Backend creates `SocialMediaAccount` with `status='active'`
3. Creates initial `FollowerHistory` from profile data
4. Analytics API returns data instead of 404

### Analytics API

```bash
# Get influencer analytics
GET /api/social-media/analytics/influencer/
Authorization: Bearer <token>

Response:
{
  "success": true,
  "data": {
    "kpi": {
      "total_followers": 50000,
      "engagement_rate": 4.5,
      "active_collaborations": 3
    },
    "growth_trends": [...],
    "platform_breakdown": {...}
  }
}
```

### Campaign Management

```bash
# Create campaign
POST /api/collaborations/campaigns/
{
  "title": "Summer Collection 2024",
  "description": "Promote our new summer line",
  "budget": 50000,
  "requirements": "Fashion influencers with 10K+ followers"
}

# List campaigns
GET /api/collaborations/campaigns/

# Apply to campaign
POST /api/collaborations/requests/
{
  "campaign": 1,
  "message": "I'd love to collaborate!"
}
```

## 🧪 Testing

### Run Tests
```bash
python manage.py test
```

### Test Specific App
```bash
python manage.py test accounts
python manage.py test social_media
```

### Create Test Data
```bash
# Create test social media accounts
python create_test_social_accounts.py

# Check account status
python check_account_status.py
```

## 🚀 Deployment

### Prepare for Production

1. **Update settings**
   ```python
   # settings.py
   DEBUG = False
   ALLOWED_HOSTS = ['your-domain.com']
   ```

2. **Set environment variables**
   ```env
   SECRET_KEY=generate-new-secret-key
   DEBUG=False
   DB_NAME=production_db
   # ... other production settings
   ```

3. **Collect static files**
   ```bash
   python manage.py collectstatic
   ```

4. **Run migrations**
   ```bash
   python manage.py migrate
   ```

### Deploy to Heroku

```bash
# Install Heroku CLI
# Login
heroku login

# Create app
heroku create collabo-backend

# Add PostgreSQL
heroku addons:create heroku-postgresql:hobby-dev

# Set environment variables
heroku config:set SECRET_KEY=your-secret-key
heroku config:set DEBUG=False

# Deploy
git push heroku main

# Run migrations
heroku run python manage.py migrate

# Create superuser
heroku run python manage.py createsuperuser
```

### Deploy to AWS/DigitalOcean

1. Set up server (Ubuntu recommended)
2. Install Python, PostgreSQL, Nginx
3. Clone repository
4. Set up virtual environment
5. Configure Gunicorn
6. Set up Nginx as reverse proxy
7. Configure SSL with Let's Encrypt

## 🔒 Security

### Best Practices
- ✅ JWT authentication
- ✅ Password hashing with Django's default
- ✅ CORS configuration
- ✅ Environment-based secrets
- ✅ SQL injection protection (Django ORM)
- ✅ XSS protection
- ✅ CSRF protection

### Production Checklist
- [ ] Set `DEBUG=False`
- [ ] Generate new `SECRET_KEY`
- [ ] Configure `ALLOWED_HOSTS`
- [ ] Use PostgreSQL instead of SQLite
- [ ] Set up HTTPS
- [ ] Configure proper CORS origins
- [ ] Set up database backups
- [ ] Configure logging
- [ ] Set up monitoring

## 📝 API Documentation

### Authentication Endpoints
- `POST /api/auth/register/` - Register new user
- `POST /api/auth/login/` - Login user
- `GET /api/auth/profile/` - Get current user profile
- `PUT /api/auth/profile/` - Update profile
- `POST /api/auth/change-password/` - Change password

### Influencer Endpoints
- `GET /api/auth/influencer-profile/` - Get influencer profile
- `PUT /api/auth/influencer-profile/` - Update influencer profile
- `GET /api/influencers/` - List all influencers
- `GET /api/influencers/<id>/` - Get influencer details

### Campaign Endpoints
- `GET /api/collaborations/campaigns/` - List campaigns
- `POST /api/collaborations/campaigns/` - Create campaign
- `GET /api/collaborations/campaigns/<id>/` - Get campaign details
- `PUT /api/collaborations/campaigns/<id>/` - Update campaign
- `DELETE /api/collaborations/campaigns/<id>/` - Delete campaign

### Collaboration Endpoints
- `GET /api/collaborations/requests/` - List collaboration requests
- `POST /api/collaborations/requests/` - Create request
- `PUT /api/collaborations/requests/<id>/` - Update request status

### Social Media Endpoints
- `GET /api/social-media/accounts/` - List connected accounts
- `POST /api/social-media/connect/` - Connect account (OAuth)
- `GET /api/social-media/analytics/influencer/` - Get analytics
- `POST /api/social-media/analytics/refresh/` - Refresh analytics

## 🐛 Troubleshooting

### Database Issues
```bash
# Reset database
python manage.py flush

# Recreate migrations
python manage.py makemigrations
python manage.py migrate
```

### Celery Not Working
```bash
# Check Redis is running
redis-cli ping  # Should return PONG

# Restart Celery
celery -A influencer_platform worker -l info
```

### Import Errors
```bash
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

## 📄 License

This project is private and proprietary.

## 👥 Contributors

- **Rinsna** - Lead Developer

## 🔗 Links

- **Backend Repository**: https://github.com/Rinsna/Collabo_backend
- **Frontend Repository**: https://github.com/Rinsna/Collabo
- **API Documentation**: (Add Swagger/Postman link)

## 📞 Support

For issues or questions, please open an issue on GitHub.

---

Built with Django and Django REST Framework
