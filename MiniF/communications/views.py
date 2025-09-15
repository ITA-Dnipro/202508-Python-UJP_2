from rest_framework import viewsets, status
from rest_framework.response import Response
from .models import ChatRoom, Message
from rest_framework.permissions import IsAuthenticated
from .serializers import ChatRoomSerializer, MessageSerializer
from django.contrib.auth import get_user_model

User = get_user_model()# UserProfile

class ConversationViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]
    def create(self, request):
        participants = request.data.get('participants', [])

        if len(participants) != 2:
            return Response({'error': 'Need exactly 2 participants'}, status=status.HTTP_400_BAD_REQUEST)

        user1 = request.user
        user2_id = participants[0] if participants[0] != user1.id else participants[1]
        user2 = User.objects.get(id=user2_id)
        #ToDo: add role check
        room, created = ChatRoom.objects.get_or_create(
            investor=user1,
            #user1 if 'Investor' in user1.roles else user2,
            startup=user2
            #user2 if 'Startup' in user2.roles else user1
        )
        serializer = ChatRoomSerializer(room)

        return Response(serializer.data, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)

    def list_messages(self, request, conversation_id=None):
        messages = Message.objects.filter(room_id=conversation_id).order_by('timestamp')
        serializer = MessageSerializer(messages, many=True)

        return Response(serializer.data)

class MessageViewSet(viewsets.ViewSet):
    def create(self, request):
        conversation_id = request.data.get('conversation_id')
        text = request.data.get('text')

        if not conversation_id or not text:
            return Response({'error': 'Conversation ID and text are required'}, status=status.HTTP_400_BAD_REQUEST)

        room = ChatRoom.objects.get(id=conversation_id)
        message = Message.objects.create(room=room, sender=request.user, receiver=room.investor if request.user == room.startup else room.startup, content=text)
        serializer = MessageSerializer(message)

        return Response(serializer.data, status=status.HTTP_201_CREATED)