# PostgreSQL Setup on Render - Complete Guide

## Overview
- Backend URL: https://collabo-backend-y2de.onrender.com
- Database: PostgreSQL (persistent, won't lose data on redeploys)
- Configuration: Auto-switches between PostgreSQL (production) and SQLite (local development)

## Step-by-Step Setup (10 minutes)

### Step 1: Create PostgreSQL Database (3 minutes)

1. Go to Render Dashboard: https://dashboard.render.com
2. Click **"New +"** → **"PostgreSQL"**
3. Configure:
   - **Name**: `collabo-database`
   - **Database**: `collabo_db`
   - **User**: `collabo_user`
   - **Region**: **Same region as your web service** (important!)
   - **PostgreSQL Version**: 16 (latest)
   - **Plan**: **Free**
4. Click **"Create Database"**
5. Wait ~1 minute for database to be created

### Step 2: Get Database Connection URL (1 minute)

1. Once database is created, click on it
2. Scroll down to **"Connections"** section
3. **Copy the "Internal Database URL"** (starts with `postgres://`)
   - Format: `postgres://user:password@hostname/database`
   - Example: `postgres://collabo_user:abc123@dpg-xyz.oregon-postgres.render.com/collabo_db`

⚠️ **Important**: Use the **Internal Database URL**, not External!

### Step 3: Add Environment Variables to Web Service (3 minutes)

1. Go to your web service: https://dashboard.render.com/web/srv-xxxxx
2. Click **"Environment"** tab on the left
3. Click **"Add Environment Variable"**
4. Add these variables one by one:

```bash
# Required Variables
SECRET_KEY=<generate-new-key-from-djecrety.ir>
DEBUG=False
ALLOWED_HOSTS=collabo-backend-y2de.onrender.com
DATABASE_URL=<paste-internal-database-url-from-step-2>
CORS_ALLOWED_ORIGINS=http://localhost:3000
PYTHON_VERSION=3.11.9
```

**Generate SECRET_KEY**: https://djecrety.ir/

5. Click **"Save Changes"**

### Step 4: Deploy (3 minutes)

1. Go to **"Manual Deploy"** section
2. Click **"Deploy latest commit"**
3. Wait for build to complete (~3-5 minutes)
4. Build will automatically:
   - Install dependencies (including psycopg2-binary for PostgreSQL)
   - Collect static files
   - Run migrations on PostgreSQL database
   - Start the server

### Step 5: Create Superuser (1 minute)

1. Once deployment is successful, go to **"Shell"** tab
2. Run this command:
```bash
python manage.py createsuperuser
```
3. Follow the prompts:
   - Username: (your choice)
   - Email: (your email)
   - Password: (your password)

### Step 6: Test API (1 minute)

Test these endpoints:
- **API Root**: https://collabo-backend-y2de.onrender.com/api/
- **Admin Panel**: https://collabo-backend-y2de.onrender.com/admin/
- **Register**: https://collabo-backend-y2de.onrender.com/api/accounts/register/

You should see JSON responses, not 500 errors! ✅

## Environment Variables Template

Copy this template and replace the values:

```bash
SECRET_KEY=django-insecure-REPLACE-WITH-KEY-FROM-DJECRETY
DEBUG=False
ALLOWED_HOSTS=collabo-backend-y2de.onrender.com
DATABASE_URL=postgres://collabo_user:PASSWORD@dpg-xxxxx.oregon-postgres.render.com/collabo_db
CORS_ALLOWED_ORIGINS=http://localhost:3000
PYTHON_VERSION=3.11.9
```

## Optional Environment Variables (Add Later)

```bash
# Stripe Payment Gateway
STRIPE_PUBLISHABLE_KEY=pk_test_your_stripe_key
STRIPE_SECRET_KEY=sk_test_your_stripe_secret

# Social Media OAuth (if using)
INSTAGRAM_CLIENT_ID=your_instagram_client_id
INSTAGRAM_CLIENT_SECRET=your_instagram_client_secret
YOUTUBE_CLIENT_ID=your_youtube_client_id
YOUTUBE_CLIENT_SECRET=your_youtube_client_secret

# Redis (if using Celery for background tasks)
REDIS_URL=redis://your-redis-url
```

## Troubleshooting

### Issue: Still getting 500 error after deploy

**Check Logs**:
1. Go to web service → **"Logs"** tab
2. Look for Python error messages
3. Common issues:
   - Missing DATABASE_URL
   - Wrong DATABASE_URL format
   - Database not in same region

**Solution**:
- Verify DATABASE_URL is set correctly
- Make sure you used **Internal Database URL**
- Check database and web service are in same region

### Issue: Database connection failed

**Error**: `could not connect to server`

**Solution**:
1. Verify database is running (check PostgreSQL dashboard)
2. Ensure you copied **Internal Database URL** (not External)
3. Check database and web service are in **same region**
4. Wait a few minutes for database to fully initialize

### Issue: SSL connection error

**Error**: `SSL connection has been closed unexpectedly`

**Solution**: Already configured with `ssl_require=True` in settings.py

### Issue: CORS errors from frontend

**Error**: `Access-Control-Allow-Origin` error in browser console

**Solution**: Update CORS_ALLOWED_ORIGINS to include your Vercel URL:
```bash
CORS_ALLOWED_ORIGINS=https://your-app.vercel.app,http://localhost:3000
```

### Issue: Migrations not running

**Solution**: Run manually in Shell:
```bash
python manage.py migrate
python manage.py showmigrations  # Check status
```

## Benefits of PostgreSQL

✅ **Persistent Data**: Data survives redeploys
✅ **Free Tier**: 90 days free, then $7/month
✅ **Production Ready**: Better performance than SQLite
✅ **Concurrent Access**: Multiple connections supported
✅ **Backups**: Automatic backups available

## Next Steps

1. ✅ PostgreSQL database created
2. ✅ Environment variables configured
3. ✅ Backend deployed successfully
4. ✅ Superuser created
5. ✅ API tested
6. 🔄 Deploy frontend to Vercel
7. 🔄 Update frontend CORS_ALLOWED_ORIGINS
8. 🔄 Test full application flow

## Quick Checklist

- [ ] PostgreSQL database created in Render
- [ ] Internal Database URL copied
- [ ] SECRET_KEY generated from djecrety.ir
- [ ] All environment variables added to web service
- [ ] Manual deploy triggered
- [ ] Build completed successfully (check Logs)
- [ ] Superuser created via Shell
- [ ] API endpoints tested and working
- [ ] Admin panel accessible

## Support Resources

- Render PostgreSQL Docs: https://render.com/docs/databases
- Django Database Docs: https://docs.djangoproject.com/en/5.0/ref/databases/
- Troubleshooting Deploys: https://render.com/docs/troubleshooting-deploys

---

**Total Setup Time**: ~10 minutes
**Cost**: Free for 90 days, then $7/month for PostgreSQL
