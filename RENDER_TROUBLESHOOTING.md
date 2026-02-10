# Render Deployment Troubleshooting

## Error: "Getting requirements to build wheel: finished with status 'error'"

This error occurs when Python packages fail to compile. Here are the solutions:

### Solution 1: Use Simplified requirements.txt (RECOMMENDED)

I've updated your `requirements.txt` to use only essential, stable packages:

```txt
Django==5.0.0
djangorestframework==3.14.0
django-cors-headers==4.3.1
djangorestframework-simplejwt==5.3.1
gunicorn==21.2.0
whitenoise==6.6.0
psycopg2-binary==2.9.9
Pillow==10.1.0
python-decouple==3.8
dj-database-url==2.1.0
requests==2.31.0
python-dateutil==2.8.2
```

**What was removed:**
- `celery` and `redis` (optional, not needed for basic functionality)
- `instaloader` and `google-api-python-client` (optional social media packages)
- `cryptography` (can cause build issues)
- `stripe` (add back if you need payment processing)

### Solution 2: Specify Python Version

In Render, add environment variable:
```
PYTHON_VERSION=3.11.0
```

### Solution 3: If Still Failing

Try even more minimal requirements:

```txt
Django==5.0.0
djangorestframework==3.14.0
django-cors-headers==4.3.1
djangorestframework-simplejwt==5.3.1
gunicorn==21.2.0
whitenoise==6.6.0
dj-database-url==2.1.0
```

Then add packages one by one to find which causes the issue.

## Common Build Errors and Fixes

### Error: "psycopg2" build fails

**Solution:** Use `psycopg2-binary` instead:
```txt
psycopg2-binary==2.9.9
```

### Error: "Pillow" build fails

**Solution:** Remove Pillow if you don't need image processing:
```txt
# Pillow==10.1.0  # Comment out
```

Or use older version:
```txt
Pillow==9.5.0
```

### Error: "cryptography" build fails

**Solution:** Remove if not essential:
```txt
# cryptography==41.0.7  # Comment out
```

### Error: Python version mismatch

**Solution:** Set Python version in Render:
```
Environment Variables:
PYTHON_VERSION=3.11.0
```

## Step-by-Step Fix Process

### 1. Update requirements.txt

Use the simplified version I provided above.

### 2. Commit and Push

```bash
cd backend
git add requirements.txt build.sh
git commit -m "Fix: Simplify requirements for Render deployment"
git push origin main
```

### 3. Redeploy on Render

Render will automatically detect the push and redeploy.

Or manually:
1. Go to Render Dashboard
2. Click your service
3. Click "Manual Deploy" → "Deploy latest commit"

### 4. Check Build Logs

1. Go to Render Dashboard
2. Click on your service
3. Click "Logs" tab
4. Watch the build process

### 5. If Still Failing

Check which package is causing the issue:

```bash
# Test locally first
python -m venv test_env
source test_env/bin/activate  # or test_env\Scripts\activate on Windows
pip install -r requirements.txt
```

If a package fails locally, it will fail on Render too.

## Alternative: Use Docker (Advanced)

If you continue having issues, consider using Docker:

### Dockerfile
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD gunicorn influencer_platform.wsgi:application --bind 0.0.0.0:$PORT
```

Then deploy as Docker container on Render.

## Current Working Configuration

### requirements.txt (Minimal)
```txt
Django==5.0.0
djangorestframework==3.14.0
django-cors-headers==4.3.1
djangorestframework-simplejwt==5.3.1
django-filter==23.5
gunicorn==21.2.0
whitenoise==6.6.0
psycopg2-binary==2.9.9
Pillow==10.1.0
python-decouple==3.8
dj-database-url==2.1.0
requests==2.31.0
python-dateutil==2.8.2
```

### build.sh
```bash
#!/usr/bin/env bash
set -o errexit

pip install --upgrade pip
pip install -r requirements.txt
python manage.py collectstatic --no-input
python manage.py migrate
```

### Environment Variables
```
PYTHON_VERSION=3.11.0
SECRET_KEY=your-secret-key
DEBUG=False
ALLOWED_HOSTS=collabo-backend-y2de.onrender.com
DATABASE_URL=postgresql://...
```

## Testing Locally Before Deploy

Always test locally first:

```bash
# Create fresh virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install requirements
pip install -r requirements.txt

# If this works, it should work on Render
```

## Contact Support

If none of these solutions work:

1. **Render Support**: https://render.com/docs/support
2. **Check Render Status**: https://status.render.com/
3. **Community Forum**: https://community.render.com/

## Quick Fix Summary

1. ✅ Use simplified `requirements.txt` (already updated)
2. ✅ Set `PYTHON_VERSION=3.11.0` in Render
3. ✅ Commit and push changes
4. ✅ Redeploy on Render
5. ✅ Check logs for success

Your deployment should work now! 🚀
