from rest_framework import serializers
from .models import ChatRoom, Message
from users.models import UserProfile


class ChatRoomSerializer(serializers.ModelSerializer):
    investor = serializers.ReadOnlyField(source="investor.username")
    startup = serializers.ReadOnlyField(source="startup.username")

    class Meta:
        model = ChatRoom
        fields = ["id", "investor", "startup", "created_at"]


class MessageSerializer(serializers.ModelSerializer):
    sender = serializers.ReadOnlyField(source="sender.username")
    receiver = serializers.ReadOnlyField(source="receiver.username")

    class Meta:
        model = Message
        fields = ["id", "room", "sender", "receiver", "content", "timestamp"]
