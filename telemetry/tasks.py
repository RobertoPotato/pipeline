"""
Celery tasks for telemetry housekeeping.
"""
import logging
from datetime import timedelta

from celery import shared_task
from django.utils import timezone

logger = logging.getLogger('pipeline')


@shared_task
def cleanup_old_logs(days=90):
    """Delete API ingestion logs older than `days` days."""
    from telemetry.models import ApiIngestionLog

    cutoff = timezone.now() - timedelta(days=days)
    count, _ = ApiIngestionLog.objects.filter(created_at__lt=cutoff).delete()
    logger.info(f'Cleaned up {count} ingestion logs older than {days} days.')
    return count
