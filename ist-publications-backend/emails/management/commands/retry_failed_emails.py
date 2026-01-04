"""
Management command to retry failed emails
Usage: python manage.py retry_failed_emails
"""

from django.core.management.base import BaseCommand
from apps.emails.services import email_service
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Retry failed emails (max 5 attempts per email)'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--count',
            type=int,
            default=50,
            help='Number of failed emails to retry'
        )
        parser.add_argument(
            '--max-retries',
            type=int,
            default=5,
            help='Maximum retry attempts'
        )
    
    def handle(self, *args, **options):
        count = options['count']
        max_retries = options['max_retries']
        
        self.stdout.write(
            self.style.SUCCESS(f'Starting retry of {count} failed emails...')
        )
        
        try:
            retried = email_service.retry_failed_emails(max_retries)
            self.stdout.write(
                self.style.SUCCESS(f'Successfully retried {retried} email(s)')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error during retry: {str(e)}')
            )
            logger.error(f"Retry command error: {str(e)}")


# Alternative scheduled task for Celery
# tasks.py
from celery import shared_task
from apps.emails.services import email_service

@shared_task
def retry_failed_emails_task():
    """Celery task to retry failed emails every 30 minutes"""
    try:
        retried = email_service.retry_failed_emails(max_retries=5)
        return f"Retried {retried} emails"
    except Exception as e:
        logger.error(f"Celery retry task failed: {str(e)}")
        return f"Error: {str(e)}"

# Add to celerybeat schedule in settings.py:
from celery.schedules import crontab

CELERY_BEAT_SCHEDULE = {
    'retry-failed-emails': {
        'task': 'apps.emails.tasks.retry_failed_emails_task',
        'schedule': crontab(minute='*/30'),  # Every 30 minutes
    },
}
