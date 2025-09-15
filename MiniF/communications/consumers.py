import json

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from django.db.utils import IntegrityError
from rest_framework.permissions import IsAuthenticated
from .models import ChatRoom, Message
from django.contrib.auth import get_user_model

User = get_user_model()

class ChatConsumer(AsyncWebsocketConsumer):

    permission_classes = [IsAuthenticated]
    """
    WebSocket consumer for a chat room.

    This consumer handles:
    - Accepting WebSocket connections and assigning users to a room group.
    - Removing users from the room group on disconnect.
    - Receiving messages from a WebSocket and broadcasting them to the group.
    - Receiving messages from the group and sending them back to the WebSocket.
    """

    async def connect(self):
        """
        Called when a WebSocket connection is ESTABLISHED.

        - Extracts the room name from the URL.
        - Joins the corresponding channel layer group.
        - Accepts the WebSocket connection.
        """
        other_user_id = self.scope['url_route']['kwargs']['other_user_id']
        self.other_user = await self.get_user(other_user_id)
        if not self.scope['user'].is_authenticated or not self.other_user:
            await self.close()
            return
        self.room = await self.get_or_create_chat_room(self.scope['user'], self.other_user)
        self.room_group_name = f'chat_{self.room.id}'
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        """
        Called when the WebSocket connection is CLOSED.

        - Removes the current channel from the room group.
        """
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        """
        Called when a message is received from the WebSocket.

        - Parses the JSON payload to extract the message.
        - Sends the message event to the room group.
        """
        data = json.loads(text_data)
        message = data.get('message')
        await self.save_message(self.room, self.scope['user'], self.other_user, message)
        await self.channel_layer.group_send(self.room_group_name, {'type': 'chat_message', 'message': message,
                                                                   'sender': self.scope['user'].username})

    async def chat_message(self, event):
        """
        Handler for messages received from the room group.

        - Extracts the message from the event.
        - Sends the message to the WebSocket as JSON.
        """
        await self.send(text_data=json.dumps({'message': event['message'], 'sender': event['sender']}))

    @database_sync_to_async
    def get_user(self, user_id):
        return User.objects.get(pk=user_id)

    @database_sync_to_async
    def get_or_create_chat_room(self, user1, user2):
        try:
            room = ChatRoom.objects.get_or_create(investor=user1 if 'Investor' in user1.roles else user2,
                                                  startup=user2 if 'Startup' in user2.roles else user1)
            return room[0]
        except IntegrityError:
            return ChatRoom.objects.get(investor=user1 if 'Investor' in user1.roles else user2,
                                        startup=user2 if 'Startup' in user2.roles else user1)

    @database_sync_to_async
    def save_message(self, room, sender, receiver, content):
        Message.objects.create(room=room, sender=sender, receiver=receiver, content=content)