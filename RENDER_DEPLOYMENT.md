# Deploy Django Backend to Render

Complete guide for deploying the Collabo backend to Render.

## Prerequisites

- GitHub account with backend repository pushed
- Render account (free tier available)
- Backend code at: https://github.com/Rinsna/Collabo_backend

## Step-by-Step Deployment

### 1. Create New Web Service on Render

1. Go to https://render.com/
2. Click **"New +"** → **"Web Service"**
3. Connect your GitHub account if not already connected
4. Select repository: **Collabo_backend**
5. Click **"Connect"**

### 2. Configure Web Service

Fill in the following settings:

#### Basic Settings
- **Name**: `collabo-backend` (or your preferred name)
- **Region**: Choose closest to your users
- **Branch**: `main`
- **Root Directory**: Leave empty (or `.` if needed)
- **Runtime**: `Python 3`

#### Build & Deploy Settings
- **Build Command**: 
  ```bash
  ./build.sh
  ```
  
- **Start Command**: 
  ```bash
  gunicorn influencer_platform.wsgi:application
  ```

#### Instance Type
- **Free** (for testing)
- **Starter** or higher (for production)

### 3. Add Environment Variables

Click **"Advanced"** → **"Add Environment Variable"**

Add these variables:

```env
# Required
SECRET_KEY=generate-a-new-secret-key-here
DEBUG=False
ALLOWED_HOSTS=your-app-name.onrender.com

# Database (Render will provide these if you add PostgreSQL)
DATABASE_URL=postgresql://user:password@host:port/dbname

# CORS (Add your frontend URL)
CORS_ALLOWED_ORIGINS=https://your-frontend.netlify.app,https://your-frontend.vercel.app

# Python Version
PYTHON_VERSION=3.11.0

# Optional: Social Media
INSTAGRAM_API_KEY=your_key
YOUTUBE_API_KEY=your_key
SOCIAL_MEDIA_ENCRYPTION_KEY=your_fernet_key

# Optional: Payment
STRIPE_SECRET_KEY=sk_live_your_key
```

**Generate SECRET_KEY:**
```python
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

### 4. Add PostgreSQL Database

1. In Render Dashboard, click **"New +"** → **"PostgreSQL"**
2. Name: `collabo-db`
3. Database: `collabo_db`
4. User: `collabo_user`
5. Region: Same as your web service
6. Plan: **Free** (for testing)
7. Click **"Create Database"**

#### Connect Database to Web Service

1. Go to your web service settings
2. Click **"Environment"**
3. Add environment variable:
   - Key: `DATABASE_URL`
   - Value: Copy from PostgreSQL "Internal Database URL"

### 5. Update settings.py for Render

Your `settings.py` should have:

```python
import os
import dj_database_url

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = config('DEBUG', default=False, cast=bool)

# Allowed hosts
ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='localhost').split(',')

# Database
DATABASES = {
    'default': dj_database_url.config(
        default=config('DATABASE_URL', default='sqlite:///db.sqlite3'),
        conn_max_age=600
    )
}

# Static files
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# CORS
CORS_ALLOWED_ORIGINS = config('CORS_ALLOWED_ORIGINS', default='http://localhost:3000').split(',')
```

### 6. Deploy

1. Click **"Create Web Service"**
2. Render will:
   - Clone your repository
   - Run `build.sh` (install dependencies, collect static, migrate)
   - Start the app with `gunicorn`
3. Wait for deployment to complete (5-10 minutes)

### 7. Verify Deployment

Once deployed, your API will be available at:
```
https://your-app-name.onrender.com
```

Test endpoints:
- Admin: `https://your-app-name.onrender.com/admin/`
- API: `https://your-app-name.onrender.com/api/`

### 8. Create Superuser

After first deployment:

1. Go to Render Dashboard → Your Web Service
2. Click **"Shell"** tab
3. Run:
   ```bash
   python manage.py createsuperuser
   ```
4. Follow prompts to create admin user

### 9. Update Frontend

Update your frontend `.env` to use the new API URL:

```env
REACT_APP_API_URL=https://your-app-name.onrender.com/api
```

Redeploy frontend.

## Configuration Files

### build.sh
```bash
#!/usr/bin/env bash
set -o errexit

pip install -r requirements.txt
python manage.py collectstatic --no-input
python manage.py migrate
```

Make it executable:
```bash
chmod +x build.sh
```

### requirements.txt
Must include:
```
Django>=6.0.2
gunicorn==21.2.0
whitenoise==6.6.0
psycopg2-binary==2.9.9
dj-database-url==2.1.0
python-decouple==3.8
```

## Environment Variables Reference

### Required
- `SECRET_KEY` - Django secret key (generate new one)
- `DEBUG` - Set to `False` for production
- `ALLOWED_HOSTS` - Your Render domain
- `DATABASE_URL` - PostgreSQL connection string (from Render)

### Optional
- `CORS_ALLOWED_ORIGINS` - Frontend URLs (comma-separated)
- `PYTHON_VERSION` - Python version (e.g., 3.11.0)
- `INSTAGRAM_API_KEY` - For social media features
- `YOUTUBE_API_KEY` - For social media features
- `STRIPE_SECRET_KEY` - For payments

## Troubleshooting

### Build Fails

**Check build logs:**
1. Go to Render Dashboard
2. Click on your service
3. Check "Logs" tab

**Common issues:**
- Missing dependencies in `requirements.txt`
- Syntax errors in `build.sh`
- Wrong Python version

**Fix:**
```bash
# Add missing package
echo "package-name==version" >> requirements.txt

# Commit and push
git add requirements.txt
git commit -m "Add missing dependency"
git push
```

### Database Connection Error

**Check:**
1. `DATABASE_URL` is set correctly
2. PostgreSQL database is running
3. Database credentials are correct

**Fix:**
1. Go to PostgreSQL database in Render
2. Copy "Internal Database URL"
3. Update `DATABASE_URL` in web service environment variables

### Static Files Not Loading

**Check:**
1. `whitenoise` is installed
2. `STATIC_ROOT` is set in settings.py
3. `collectstatic` runs in build.sh

**Fix:**
```python
# settings.py
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Add to MIDDLEWARE (after SecurityMiddleware)
'whitenoise.middleware.WhiteNoiseMiddleware',
```

### CORS Errors

**Check:**
1. `CORS_ALLOWED_ORIGINS` includes your frontend URL
2. Frontend is using correct API URL

**Fix:**
```python
# settings.py
CORS_ALLOWED_ORIGINS = [
    'https://your-frontend.netlify.app',
    'https://your-frontend.vercel.app',
]

# Or from environment
CORS_ALLOWED_ORIGINS = config('CORS_ALLOWED_ORIGINS', default='').split(',')
```

### App Crashes on Start

**Check logs:**
```bash
# In Render Shell
python manage.py check
python manage.py migrate --check
```

**Common causes:**
- Missing migrations
- Database connection issues
- Import errors

### Slow Cold Starts (Free Tier)

Free tier services spin down after 15 minutes of inactivity.

**Solutions:**
1. Upgrade to paid tier
2. Use a service like UptimeRobot to ping your app
3. Accept the cold start delay

## Post-Deployment

### 1. Test API Endpoints
```bash
# Health check
curl https://your-app-name.onrender.com/api/

# Register user
curl -X POST https://your-app-name.onrender.com/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","username":"test","password":"test123","password_confirm":"test123","user_type":"influencer"}'
```

### 2. Monitor Logs
- Go to Render Dashboard
- Click on your service
- Monitor "Logs" tab for errors

### 3. Set Up Custom Domain (Optional)
1. Go to service settings
2. Click "Custom Domain"
3. Add your domain
4. Update DNS records as instructed

### 4. Enable HTTPS
Render provides free SSL certificates automatically.

### 5. Set Up Monitoring
- Use Render's built-in metrics
- Set up alerts for downtime
- Monitor database usage

## Updating Your App

### Deploy New Changes
```bash
# Make changes locally
git add .
git commit -m "Update feature"
git push origin main
```

Render will automatically:
1. Detect the push
2. Run build.sh
3. Deploy new version

### Manual Deploy
1. Go to Render Dashboard
2. Click "Manual Deploy"
3. Select branch
4. Click "Deploy"

## Cost Optimization

### Free Tier Limits
- Web Service: Spins down after 15 min inactivity
- PostgreSQL: 1GB storage, 97 hours/month
- Bandwidth: 100GB/month

### Upgrade When Needed
- **Starter ($7/month)**: No spin down, better performance
- **Standard ($25/month)**: More resources, better for production

## Security Checklist

- [ ] `DEBUG=False` in production
- [ ] New `SECRET_KEY` generated
- [ ] `ALLOWED_HOSTS` configured
- [ ] HTTPS enabled (automatic on Render)
- [ ] CORS properly configured
- [ ] Database credentials secure
- [ ] Environment variables set
- [ ] Admin panel secured

## Support

- **Render Docs**: https://render.com/docs
- **Django Deployment**: https://docs.djangoproject.com/en/stable/howto/deployment/
- **GitHub Issues**: https://github.com/Rinsna/Collabo_backend/issues

---

Your Django backend is now live on Render! 🚀
