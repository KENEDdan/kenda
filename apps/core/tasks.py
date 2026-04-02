import logging
from celery import shared_task

logger = logging.getLogger('kenda')


@shared_task
def send_welcome_email(user_id: str, email: str) -> str:
    """
    Placeholder welcome email task.
    Will be implemented fully in Phase 7 (Communications).
    """
    logger.info('Sending welcome email to %s (id=%s)', email, user_id)
    return f'Welcome email queued for {email}'