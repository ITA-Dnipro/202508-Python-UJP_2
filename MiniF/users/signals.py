import logging 
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import UserProfile
from .tasks import send_welcome_email

logger = logging.getLogger(__name__)

@receiver(post_save, sender=UserProfile)
def send_welcome_email_on_creation(sender, instance, created, **kwargs):
    """
    Sends a welcome email when a new UserProfile is created.
    """
    if created:
        logger.info(f"Triggering welcome email for new user: {instance.email}")
        send_welcome_email.delay(instance.id)