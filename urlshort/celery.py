from __future__ import absolute_import, unicode_literals
from celery import Celery
import os
from celery.schedules import crontab

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "urlshort.settings")
app = Celery("urlshort")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()

app.conf.beat_schedule = {
    'delete-expired-urls-every-hour': {
        'task': 'urlgen.tasks.delete_expired_urls',  # Use the task path
        'schedule': crontab(minute=0, hour='*'),  # Run the task at 0th miunte of every hour
    },
}