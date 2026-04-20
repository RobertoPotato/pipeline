"""
Celery application configuration for PipelineGuard.

Auto-discovers tasks from all installed Django apps.
"""
import os

from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pipeline.settings')

app = Celery('pipeline')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()
