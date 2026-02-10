# Render Backend Setup Guide

## Current Status
- Backend URL: https://collabo-backend-y2de.onrender.com
- Status: Internal Server Error (500) - Missing Configuration

## Step-by-Step Fix

### 1. Create PostgreSQL Database in Render

1. Go to Render Dashboard: https://dashboard.render.com
2. Click "New +" → "PostgreSQL"
3. Configure:
   - Name: `collabo-database`
   - Database: `collabo_db`
   - User: `collabo_user`
   - Region: Same as your web service
   - Plan: Free
4. Click "Create Database"
5. **Copy the Internal Database URL** (starts with `postgres://`)

### 2. Add Environment Variables to Web Service

Go to your web service settings and add these environment variables:

#### Required Variables:

```bash
# Django Secret Key (Generate a new one!)
SECRET_KEY=your-super-secret-key-here-change-this-now

# Debug Mode (MUST be False in production)
DEBUG=False

# Allowed Hosts (Your Render domain)
ALLOWED_HOSTS=collabo-backend-y2de.onrender.com

# Database URL (Paste from PostgreSQL database)
DATABASE_URL=postgres://collabo_user:password@hostname/collabo_db

# CORS Origins (Your Vercel frontend URL)
CORS_ALLOWED_ORIGINS=https://your-frontend.vercel.app,http://localhost:3000

# Python Version
PYTHON_VERSION=3.11.9
```

#### Optional Variables (Can add later):

```bash
# Stripe Payment (if using payments)
STRIPE_PUBLISHABLE_KEY=pk_test_your_key
STRIPE_SECRET_KEY=sk_test_your_key

# Social Media APIs (if using OAuth)
INSTAGRAM_CLIENT_ID=your_instagram_client_id
INSTAGRAM_CLIENT_SECRET=your_instagram_client_secret
YOUTUBE_CLIENT_ID=your_youtube_client_id
YOUTUBE_CLIENT_SECRET=your_youtube_client_secret

# Redis (if using Celery - optional for now)
REDIS_URL=redis://your-redis-url
```

### 3. Generate a Strong SECRET_KEY

Run this Python command locally to generate a secure key:

```python
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

Or use this online: https://djecrety.ir/

### 4. Trigger Redeploy

After adding environment variables:
1. Go to your web service
2. Click "Manual Deploy" → "Deploy latest commit"
3. Wait for build to complete

### 5. Run Database Migrations

Once deployed successfully:
1. Go to your web service
2. Click "Shell" tab
3. Run these commands:

```bash
python manage.py migrate
python manage.py createsuperuser
```

### 6. Test the API

Test these endpoints:
- Health check: https://collabo-backend-y2de.onrender.com/api/
- Admin panel: https://collabo-backend-y2de.onrender.com/admin/
- Register: https://collabo-backend-y2de.onrender.com/api/accounts/register/

## Quick Checklist

- [ ] PostgreSQL database created in Render
- [ ] DATABASE_URL copied from PostgreSQL
- [ ] SECRET_KEY generated and added
- [ ] DEBUG=False set
- [ ] ALLOWED_HOSTS set to your Render domain
- [ ] CORS_ALLOWED_ORIGINS includes your frontend URL
- [ ] Environment variables saved
- [ ] Manual redeploy triggered
- [ ] Build completed successfully
- [ ] Migrations run via Shell
- [ ] Superuser created
- [ ] API endpoints tested

## Common Issues

### Issue: Still getting 500 error
**Solution**: Check Render logs for specific error message
- Go to web service → Logs tab
- Look for Python traceback
- Common causes: Missing env vars, database connection failed

### Issue: Database connection failed
**Solution**: Verify DATABASE_URL
- Make sure you copied the **Internal Database URL** from PostgreSQL
- Format: `postgres://user:password@hostname/database`
- Check database is in same region as web service

### Issue: CORS errors from frontend
**Solution**: Update CORS_ALLOWED_ORIGINS
- Must include your Vercel frontend URL
- Format: `https://your-app.vercel.app,http://localhost:3000`
- No trailing slashes

### Issue: Static files not loading
**Solution**: Already configured with whitenoise
- Static files are served automatically
- No additional configuration needed

## Next Steps After Backend is Working

1. Deploy frontend to Vercel
2. Update frontend .env with backend URL
3. Test full authentication flow
4. Test API endpoints from frontend
5. Add optional features (Stripe, Social Media OAuth)

## Support

If you encounter issues:
1. Check Render logs for error messages
2. Verify all environment variables are set correctly
3. Ensure PostgreSQL database is running
4. Test API endpoints with curl or Postman
