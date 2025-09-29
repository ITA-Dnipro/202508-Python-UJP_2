from django.db import models
from django.utils import timezone

from mongoengine import Document, DateTimeField, StringField, LongField

from users.models import UserProfile


class ChatRoom(models.Model):
    """
    model for conversation between users (investor and startup).
    Prevents duplicate rooms via a unique constraint.
    """

    investor = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name="investor_rooms")
    startup = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name="startup_rooms")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        """
        avoiding duplicate rooms
        """

        constraints = [models.UniqueConstraint(fields=["investor", "startup"], name="unique_investor_startup_room")]

    def __str__(self):
        return f"Room between {self.investor.username} and {self.startup.username}"


class Message(Document):
    """
    a model for messages in a conversation.
    """

    room_id = LongField(required=True)
    sender_id = LongField(required=True)
    receiver_id = LongField(required=True)
    content = StringField(required=True)
    timestamp = DateTimeField(default=timezone.now)

    meta = {
        "indexes": [("room_id", "timestamp")],
    }

    def __str__(self):
        try:
            return f"Message from {self.sender_id} to {self.receiver_id} at {self.timestamp}"
        except UserProfile.DoesNotExist:
            return f"Message with IDs (sender={self.sender_id}, receiver={self.receiver_id}) at {self.timestamp}"
