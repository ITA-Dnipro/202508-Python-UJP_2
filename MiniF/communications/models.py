from mongoengine import Document, DateTimeField, StringField, IntField
from django.db import models
from users.models import UserProfile
import datetime


class ChatRoom(models.Model):
    """
    model for conversation between users (investor and startup).
    """

    investor = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name="investor_rooms")
    startup = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name="startup_rooms")
    created_at = models.DateTimeField(auto_now_add=True)

    """
    avoiding duplicate rooms
    """

    class Meta:
        constraints = [models.UniqueConstraint(fields=["investor", "startup"], name="unique_investor_startup_room")]

    def __str__(self):
        return f"Room between {self.investor.username} and {self.startup.username}"


class Message(Document):
    """
    a model for messages in a conversation.
    """

    room_id = IntField(required=True)
    sender_id = IntField(required=True)
    receiver_id = IntField(required=True)
    content = StringField(required=True)
    timestamp = DateTimeField(default=datetime.datetime.now)

    meta = {
        "indexes": [("room_id", "timestamp")],  # Додаємо композитний індекс
    }

    def __str__(self):
        try:
            sender = UserProfile.objects.get(id=self.sender_id)
            receiver = UserProfile.objects.get(id=self.receiver_id)
            return f"Message from {sender.username} to {receiver.username} at {self.timestamp}"
        except UserProfile.DoesNotExist:
            return f"Message with IDs (sender={self.sender_id}, receiver={self.receiver_id}) at {self.timestamp}"
