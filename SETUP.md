# Backend Quick Setup Guide

## Prerequisites
- Python 3.8 or higher
- pip (Python package manager)
- PostgreSQL (optional, SQLite works for development)
- Redis (optional, for Celery tasks)

## Quick Start

### 1. Clone Repository
```bash
git clone https://github.com/Rinsna/Collabo_backend.git
cd Collabo_backend
```

### 2. Create Virtual Environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment
```bash
# Copy example env file
cp .env.example .env

# Edit .env file
# At minimum, generate a new SECRET_KEY
```

**Generate SECRET_KEY:**
```python
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

### 5. Run Migrations
```bash
python manage.py migrate
```

### 6. Create Superuser
```bash
python manage.py createsuperuser
```

### 7. Run Development Server
```bash
python manage.py runserver
```

API will be available at: http://localhost:8000

## Environment Configuration

### Minimal .env (Development)
```env
SECRET_KEY=your-generated-secret-key-here
DEBUG=True
```

### Full .env (Production)
```env
# Django
SECRET_KEY=your-secret-key
DEBUG=False
ALLOWED_HOSTS=your-domain.com,www.your-domain.com

# Database (PostgreSQL)
DB_NAME=collabo_db
DB_USER=postgres
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=5432

# Redis
REDIS_URL=redis://localhost:6379

# Social Media (Optional)
INSTAGRAM_API_KEY=your_key
YOUTUBE_API_KEY=your_key
SOCIAL_MEDIA_ENCRYPTION_KEY=your_fernet_key

# Payment (Optional)
STRIPE_SECRET_KEY=sk_test_your_key
```

## Database Setup

### Using SQLite (Default - Development)
No additional setup needed. Database file `db.sqlite3` will be created automatically.

### Using PostgreSQL (Production)
```bash
# Install PostgreSQL
# Create database
createdb collabo_db

# Update .env with PostgreSQL credentials
DB_NAME=collabo_db
DB_USER=postgres
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=5432

# Run migrations
python manage.py migrate
```

## Optional: Celery Setup

For async tasks (social media syncing):

### 1. Install Redis
```bash
# Windows: Download from https://github.com/microsoftarchive/redis/releases
# Linux: sudo apt-get install redis-server
# Mac: brew install redis
```

### 2. Start Redis
```bash
redis-server
```

### 3. Start Celery Worker (in new terminal)
```bash
# Activate virtual environment first
celery -A influencer_platform worker -l info
```

### 4. Start Celery Beat (in another terminal)
```bash
# Activate virtual environment first
celery -A influencer_platform beat -l info
```

## Testing the API

### 1. Access Admin Panel
http://localhost:8000/admin/
Login with superuser credentials

### 2. Test API Endpoints
```bash
# Register user
curl -X POST http://localhost:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "username": "testuser",
    "password": "testpass123",
    "password_confirm": "testpass123",
    "user_type": "influencer"
  }'

# Login
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "testpass123"
  }'
```

### 3. Create Test Data
```bash
# Create test social media accounts
python create_test_social_accounts.py

# Check account status
python check_account_status.py
```

## Common Issues

### Port Already in Use
```bash
# Kill process on port 8000
# Windows
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Linux/Mac
lsof -ti:8000 | xargs kill -9
```

### Migration Errors
```bash
# Reset migrations
python manage.py migrate --fake-initial

# Or recreate database
rm db.sqlite3
python manage.py migrate
```

### Module Not Found
```bash
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

### Celery Connection Error
```bash
# Check Redis is running
redis-cli ping  # Should return PONG

# If not, start Redis
redis-server
```

## Development Workflow

### 1. Make Changes
Edit files in respective apps (accounts, collaborations, etc.)

### 2. Create Migrations (if models changed)
```bash
python manage.py makemigrations
python manage.py migrate
```

### 3. Test Changes
```bash
python manage.py test
```

### 4. Run Server
```bash
python manage.py runserver
```

## API Endpoints

### Authentication
- `POST /api/auth/register/` - Register
- `POST /api/auth/login/` - Login
- `GET /api/auth/profile/` - Get profile
- `PUT /api/auth/profile/` - Update profile

### Influencers
- `GET /api/auth/influencer-profile/` - Get influencer profile
- `PUT /api/auth/influencer-profile/` - Update influencer profile
- `GET /api/influencers/` - List influencers

### Campaigns
- `GET /api/collaborations/campaigns/` - List campaigns
- `POST /api/collaborations/campaigns/` - Create campaign
- `GET /api/collaborations/campaigns/<id>/` - Get campaign

### Social Media
- `GET /api/social-media/accounts/` - List accounts
- `GET /api/social-media/analytics/influencer/` - Get analytics

## Next Steps

1. ✅ Backend running on http://localhost:8000
2. ✅ Admin panel accessible at http://localhost:8000/admin/
3. ✅ API endpoints ready for frontend
4. 📱 Connect frontend at http://localhost:3000

## Production Deployment

See README.md for detailed production deployment instructions.

## Need Help?

- Check README.md for detailed documentation
- Open an issue on GitHub
- Check Django documentation: https://docs.djangoproject.com/

---

Happy coding! 🚀
