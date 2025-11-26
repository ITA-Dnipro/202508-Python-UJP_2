import logging
from django.utils import timezone
from notifications.models import Notification, NotificationType
from profiles.models import InvestorProfile, StartupProfile

logger = logging.getLogger(__name__)

def send_notification(event: dict):
    """
    Create Notification entry from RMQ event payload.
    """
    event_type = event.get("event_type")
    recipient_id = event.get("recipient_id")
    message = event.get("message", "")
    title = event.get("title", "")
    reference_id = event.get("reference_id")

    # get or create NotificationType
    notif_type, _ = NotificationType.objects.get_or_create(
        name=event["event_type"]
    )

    # determine if recipient is investor or startup
    investor = None
    startup = None

    try:
        investor = InvestorProfile.objects.filter(user_id=recipient_id).first()
        if not investor:
            startup = StartupProfile.objects.filter(user_id=recipient_id).first()
    except Exception as e:
        logger.error(f"Failed to load recipient profile: {e}")

    if not investor and not startup:
        logger.error(f"No profile found for recipient_id={recipient_id}")
        return

    Notification.objects.create(
        investor=investor,
        startup=startup,
        notification_type=notif_type,
        message=message,
        is_read=False,
        created_at=timezone.now(),
    )

    logger.info(f"Notification created for recipient={recipient_id}")
