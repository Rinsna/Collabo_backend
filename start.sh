#!/bin/bash

# Exit on any error
set -o errexit

echo ">>> RUNNING RUNTIME STARTUP SCRIPT..."

# Move to backend directory
cd /opt/render/project/src/backend || cd /opt/render/project/src

# Run migrations (This time on the REAL persistent disk!)
echo ">>> Applying migrations..."
python manage.py migrate --noinput

# Run Seeding (This time on the REAL persistent disk!)
echo ">>> Seeding initial data..."
python scripts/seed_data.py
python scripts/seed_influencers.py
python scripts/seed_superuser.py

# Final Startup
echo ">>> Starting Gunicorn server..."
gunicorn influencer_platform.wsgi:application
