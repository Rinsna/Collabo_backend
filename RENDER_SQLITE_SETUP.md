# Render Backend Setup with SQLite

## Current Status
- Backend URL: https://collabo-backend-y2de.onrender.com
- Database: SQLite (db.sqlite3)
- Status: Needs environment variables

## Important Note About SQLite on Render

⚠️ **SQLite Limitation**: Render's free tier has ephemeral storage, meaning your SQLite database will be reset on every deploy or when the service restarts. For production, consider:
- Using Render's persistent disk (paid feature)
- Or switching to PostgreSQL (free tier available)

For now, SQLite will work but data will be lost on redeploys.

## Setup Steps (5 minutes)

### Step 1: Add Environment Variables

Go to your Render web service → Environment tab and add:

```bash
# Django Secret Key (Generate a new one!)
SECRET_KEY=your-super-secret-key-here

# Debug Mode (False for production)
DEBUG=False

# Allowed Hosts (Your Render domain)
ALLOWED_HOSTS=collabo-backend-y2de.onrender.com

# CORS Origins (Your frontend URL)
CORS_ALLOWED_ORIGINS=http://localhost:3000

# Python Version
PYTHON_VERSION=3.11.9
```

**Generate SECRET_KEY**: https://djecrety.ir/

### Step 2: Redeploy

1. Click "Manual Deploy" → "Deploy latest commit"
2. Wait for build to complete (~3-5 minutes)
3. Build script will automatically:
   - Install dependencies
   - Collect static files
   - Run migrations
   - Create db.sqlite3

### Step 3: Create Superuser

After successful deployment:
1. Go to your web service → Shell tab
2. Run:
```bash
python manage.py createsuperuser
```
3. Follow prompts to create admin account

### Step 4: Test API

Visit these URLs:
- API Root: https://collabo-backend-y2de.onrender.com/api/
- Admin Panel: https://collabo-backend-y2de.onrender.com/admin/
- Register: https://collabo-backend-y2de.onrender.com/api/accounts/register/

## Quick Environment Variables Template

Copy and paste these, then replace the values:

```
SECRET_KEY=django-insecure-REPLACE-WITH-GENERATED-KEY
DEBUG=False
ALLOWED_HOSTS=collabo-backend-y2de.onrender.com
CORS_ALLOWED_ORIGINS=http://localhost:3000
PYTHON_VERSION=3.11.9
```

## Optional Variables (Add Later)

```bash
# Stripe Payment
STRIPE_PUBLISHABLE_KEY=pk_test_your_key
STRIPE_SECRET_KEY=sk_test_your_key

# Social Media APIs
INSTAGRAM_CLIENT_ID=your_instagram_client_id
INSTAGRAM_CLIENT_SECRET=your_instagram_client_secret
YOUTUBE_CLIENT_ID=your_youtube_client_id
YOUTUBE_CLIENT_SECRET=your_youtube_client_secret
```

## Troubleshooting

### Still getting 500 error?
1. Check Render Logs tab for error details
2. Verify all environment variables are set
3. Make sure SECRET_KEY is set (not the default)
4. Ensure ALLOWED_HOSTS includes your Render domain

### Database resets on deploy?
This is normal with SQLite on Render's free tier. Options:
1. Add persistent disk (paid): https://render.com/docs/disks
2. Switch to PostgreSQL (free tier available)
3. Accept data loss on redeploys (for testing only)

### CORS errors from frontend?
Update CORS_ALLOWED_ORIGINS to include your Vercel URL:
```
CORS_ALLOWED_ORIGINS=https://your-app.vercel.app,http://localhost:3000
```

## Next Steps

1. ✅ Add environment variables
2. ✅ Redeploy backend
3. ✅ Create superuser
4. ✅ Test API endpoints
5. 🔄 Deploy frontend to Vercel
6. 🔄 Update frontend .env with backend URL
7. 🔄 Test full application

## Upgrading to Persistent Storage (Optional)

If you want to keep your data between deploys:

### Option 1: Add Persistent Disk (Paid)
1. Go to web service → Disks tab
2. Add disk with mount path: `/opt/render/project/src`
3. Redeploy

### Option 2: Use PostgreSQL (Free)
1. Create PostgreSQL database in Render
2. Update settings.py to use DATABASE_URL
3. Add DATABASE_URL environment variable
4. Redeploy

For now, SQLite works fine for testing!
