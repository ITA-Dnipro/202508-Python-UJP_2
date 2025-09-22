import json
import datetime

from django.core.exceptions import ObjectDoesNotExist
from django.db.utils import IntegrityError
from django.utils import timezone
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken, AuthenticationFailed
from pymongo.errors import PyMongoError

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer

from users.models import UserProfile
from MiniF.settings import env
from .models import ChatRoom, Message
User = UserProfile


class ChatConsumer(AsyncWebsocketConsumer):
    """
    WebSocket consumer for a chat room.

    This consumer handles:
    - Accepting WebSocket connections and assigning users to a room group.
    - Removing users from the room group on disconnect.
    - Receiving messages from a WebSocket and broadcasting them to the group.
    - Receiving messages from the group and sending them back to the WebSocket.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.room = None
        self.room_group_name = None

    async def connect(self):
        """
        Called when a WebSocket connection is ESTABLISHED.

        - Extracts the room name from the URL.
        - Joins the corresponding channel layer group.
        - Accepts the WebSocket connection.
        """
        query_string = self.scope["query_string"].decode()
        token = None
        for param in query_string.split("&"):
            if param.startswith("token="):
                token = param.split("=")[1]
                break

        if not token:
            await self.close()
            return

        try:
            auth = JWTAuthentication()
            validated_token = auth.get_validated_token(token)
            user = await database_sync_to_async(auth.get_user)(validated_token)
            self.scope["user"] = user
        except (InvalidToken, AuthenticationFailed, ObjectDoesNotExist):
            await self.close()
            return

        room_id = self.scope["url_route"]["kwargs"]["room_id"]
        self.room = await self.get_room(room_id)
        if not self.room:
            await self.close()
            return

        is_participant = await self.is_user_participant()
        if not is_participant:
            await self.close()
            return

        self.room_group_name = f"chat_{self.room.id}"
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        """
        Called when the WebSocket connection is CLOSED.

        - Removes the current channel from the room group.
        """
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)
        if hasattr(self, "mongo_client"):
            self.mongo_client.close()

    async def receive(self, text_data):
        """
        Called when a message is received from the WebSocket.

        - Parses the JSON payload to extract the message.
        - Sends the message event to the room group.
        """
        data = json.loads(text_data)
        message = data.get("message")
        receiver = await self.get_receiver()
        await self.save_message(self.room, self.scope["user"], receiver, message)
        await self.channel_layer.group_send(
            self.room_group_name, {"type": "chat_message", "message": message, "sender": self.scope["user"].username}
        )

    async def chat_message(self, event):
        """
        Handler for messages received from the room group.

        - Extracts the message from the event.
        - Sends the message to the WebSocket as JSON.
        """
        await self.send(text_data=json.dumps({"message": event["message"], "sender": event["sender"]}))

    @database_sync_to_async
    def get_room(self, room_id):
        """Retrieve a chat room by ID."""
        try:
            return ChatRoom.objects.get(id=room_id)
        except ChatRoom.DoesNotExist:
            return None

    @database_sync_to_async
    def is_user_participant(self):
        """Check if the user is a participant in the room."""
        if not self.room:
            return False
        return self.scope["user"] in [self.room.investor, self.room.startup]

    @database_sync_to_async
    def get_receiver(self):
        """Get the receiver user based on the current user."""
        if not self.room:
            return None
        current_user = self.scope["user"]
        return self.room.startup if current_user == self.room.investor else self.room.investor

    @database_sync_to_async
    def get_user(self, user_id):
        """
        Handles broadcasting messages to WebSocket clients.

        - Sends the message and sender information to the client as JSON.
        """
        return User.objects.get(pk=user_id)

    @database_sync_to_async
    def get_or_create_chat_room(self, user1, user2):
        """
        Retrieves or creates a chat room between two users.

        Args:
            user1 (User): The first user.
            user2 (User): The second user.

        Returns:
            ChatRoom: The existing or newly created chat room.
        """
        try:
            room = ChatRoom.objects.get_or_create(
                investor=user1,
                startup=user2,
            )
            return room[0]
        except IntegrityError:
            return ChatRoom.objects.get(
                investor=user1,
                startup=user2,
            )

    @database_sync_to_async
    def save_message(self, room, sender, receiver, content):
        """
        Saves a message to the database.

        Args:
            room (ChatRoom): The chat room where the message is sent.
            sender (User): The sender of the message.
            receiver (User): The receiver of the message.
            content (str): The message content.

        Returns:
            Message: The created message object.
        """
        try:
            message = Message(
                room_id=room.pk,
                sender_id=sender.pk,
                receiver_id=receiver.pk,
                content=content,
                timestamp=timezone.now(),
            )
            message.save()
            if not message.id:
                raise PyMongoError("Message not saved")
        except PyMongoError as e:
            raise PyMongoError(f"Failed to save message: {str(e)}")
