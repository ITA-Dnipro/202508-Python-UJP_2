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
    sender_username = serializers.SerializerMethodField()
    receiver_username = serializers.SerializerMethodField()
    room_id = serializers.IntegerField()

    class Meta:
        model = Message
        fields = ["id", "room_id", "sender_username", "receiver_username", "content", "timestamp"]

    def get_sender_username(self, obj):
        try:
            user = UserProfile.objects.get(id=obj.sender_id)
            return user.username
        except UserProfile.DoesNotExist:
            return None

    def get_receiver_username(self, obj):
        try:
            user = UserProfile.objects.get(id=obj.receiver_id)
            return user.username
        except UserProfile.DoesNotExist:
            return None
