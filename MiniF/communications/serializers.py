from rest_framework import serializers

from users.models import UserProfile

from .models import ChatRoom, Message


class ChatRoomSerializer(serializers.ModelSerializer):
    """Serializer for ChatRoom model with read-only investor and startup usernames."""

    investor = serializers.ReadOnlyField(source="investor.username")
    startup = serializers.ReadOnlyField(source="startup.username")

    class Meta:
        model = ChatRoom
        fields = ["id", "investor", "startup", "created_at"]


class MessageSerializer(serializers.Serializer):
    """Serializer for Message model with sender and receiver usernames."""

    sender_username = serializers.SerializerMethodField()
    receiver_username = serializers.SerializerMethodField()
    room_id = serializers.IntegerField()
    sender_id = serializers.IntegerField()
    receiver_id = serializers.IntegerField()
    content = serializers.CharField()
    timestamp = serializers.DateTimeField(read_only=True)

    def get_sender_username(self, obj):
        """Retrieve the username of the sender."""
        try:
            user = UserProfile.objects.get(id=obj.sender_id)
            return user.username
        except UserProfile.DoesNotExist:
            return None

    def get_receiver_username(self, obj):
        """Retrieve the username of the receiver."""
        try:
            user = UserProfile.objects.get(id=obj.receiver_id)
            return user.username
        except UserProfile.DoesNotExist:
            return None
