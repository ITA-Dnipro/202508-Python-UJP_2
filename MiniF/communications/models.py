from django.db import models
from users.models import UserProfile


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
        unique_together = ["investor", "startup"]

    def __str__(self):
        return f"Room between {self.investor.username} and {self.startup.username}"


class Message(models.Model):
    """
    a model for messages in a conversation.
    """

    room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, related_name="messages")
    sender = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name="sent_messages")
    receiver = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name="received_messages")
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Message from {self.sender.username} to {self.receiver.username} at {self.timestamp}"
