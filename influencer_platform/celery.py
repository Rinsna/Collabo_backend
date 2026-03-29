import os
from celery import Celery
from celery.schedules import crontab
from django.conf import settings

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'influencer_platform.settings')

app = Celery('influencer_platform')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django apps.
app.autodiscover_tasks()

# Celery Beat schedule for periodic tasks
app.conf.beat_schedule = {
    'periodic-follower-sync': {
        'task': 'social_media.tasks.periodic_follower_sync',
        'schedule': crontab(minute='*/15'),  # Every 15 minutes
    },
    'schedule-follower-updates': {
        'task': 'social_media.tasks.schedule_follower_updates',
        'schedule': crontab(minute='*/30'),  # Every 30 minutes
    },
}

app.conf.timezone = 'UTC'

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')