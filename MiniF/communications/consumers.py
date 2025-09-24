import json
from channels.generic.websocket import AsyncWebsocketConsumer

# pylint: disable=W0201
# pylint: disable=W0237,W0613
# pylint: disable=W0221


class ChatConsumer(AsyncWebsocketConsumer):
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
        self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
        self.room_group_name = f"chat_{self.room_name}"

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
        text_data_json = json.loads(text_data)
        message = text_data_json["message"]

        await self.channel_layer.group_send(self.room_group_name, {"type": "chat.message", "message": message})

    async def chat_message(self, event):
        """
        Handler for messages received from the room group.

        - Extracts the message from the event.
        - Sends the message to the WebSocket as JSON.
        """
        message = event["message"]
        await self.send(text_data=json.dumps({"message": message}))
