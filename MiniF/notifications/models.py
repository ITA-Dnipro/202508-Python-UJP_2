from django.db import models
from django.conf import settings
from profiles.models import StartupProfile, InvestorProfile


class NotificationType(models.Model):
    """
    Model for type of notification
    """
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class Notification(models.Model):
    """
    Model for notifications.
    """
    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notifications'
    )
    investor = models.ForeignKey(
        InvestorProfile,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    startup = models.ForeignKey(
        StartupProfile,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    notification_type = models.ForeignKey(
        NotificationType,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="notifications"
    )
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['recipient', 'is_read']),
        ]

    def __str__(self):
        return f"Notification for {self.recipient.username}: {self.notification_type.type if self.notification_type else 'No Type'}"
