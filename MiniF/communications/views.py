from django.db.models import Q
from django.shortcuts import render

from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.exceptions import NotFound, PermissionDenied, ValidationError
from rest_framework.response import Response

from users.models import UserProfile
from users.permissions import IsStartupRole, IsInvestorRole

from .models import ChatRoom, Message
from .serializers import ChatRoomSerializer, MessageSerializer


def get_user_and_role_from_headers(request):
    """Helper: extract user and role from Krakend headers"""
    user_id = request.META.get("HTTP_USER_ID")
    role = request.META.get("HTTP_ROLE")

    if not user_id or not role:
        raise PermissionDenied("Missing authentication headers from Krakend")

    try:
        user = UserProfile.objects.get(id=user_id)
    except UserProfile.DoesNotExist:
        raise PermissionDenied("User not found")

    return user, role


class ConversationViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user, _ = get_user_and_role_from_headers(self.request)
        return ChatRoom.objects.filter(Q(investor=user) | Q(startup=user))

    def create(self, request):
        try:
            # Auth via Krakend headers
            current_user, role = get_user_and_role_from_headers(request)

            username = request.data.get("username")
            if not username:
                return Response({"error": "Username is required"}, status=status.HTTP_400_BAD_REQUEST)

            # Find the other user
            try:
                other_user = UserProfile.objects.get(username=username)
            except UserProfile.DoesNotExist:
                return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

            if current_user == other_user:
                return Response({"error": "Cannot chat with yourself"}, status=status.HTTP_400_BAD_REQUEST)

            if role == "startup":
                room = ChatRoom.objects.filter(
                    investor=other_user, startup=current_user
                ).first() or ChatRoom.objects.create(
                    investor=other_user, startup=current_user
                )
            elif role == "investor":
                room = ChatRoom.objects.filter(
                    investor=current_user, startup=other_user
                ).first() or ChatRoom.objects.create(
                    investor=current_user, startup=other_user
                )
            else:
                return Response({"error": f"Invalid role: {role}"}, status=status.HTTP_400_BAD_REQUEST)

            serializer = ChatRoomSerializer(room)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        except PermissionDenied as e:
            return Response({"error": str(e)}, status=status.HTTP_401_UNAUTHORIZED)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=True, methods=["get"])
    def messages(self, request, pk=None):
        try:
            messages = Message.objects.filter(room_id=pk).order_by("timestamp")
            serializer = MessageSerializer(messages, many=True)
            return Response(serializer.data)
        except ChatRoom.DoesNotExist:
            raise NotFound("Conversation not found")


class MessageViewSet(viewsets.ModelViewSet):
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user, _ = get_user_and_role_from_headers(self.request)
        return Message.objects.filter(
            room__in=ChatRoom.objects.filter(Q(investor=user) | Q(startup=user))
        ).order_by("-created_at")

    def perform_create(self, serializer):
        user, role = get_user_and_role_from_headers(self.request)
        room_id = self.request.data.get("room")

        if not room_id:
            raise ValidationError({"room": "Room ID is required"})

        try:
            room = ChatRoom.objects.get(id=room_id)
        except ChatRoom.DoesNotExist:
            raise ValidationError({"room": "Chat room not found"})

        if user not in [room.investor, room.startup]:
            raise PermissionDenied("You are not a participant in this room.")

        if role == "startup" and room.startup != user:
            raise PermissionDenied("Startups can only send messages as the startup.")
        if role == "investor" and room.investor != user:
            raise PermissionDenied("Investors can only send messages as the investor.")

        receiver = room.startup if room.investor == user else room.investor
        serializer.save(sender=user, receiver=receiver, room=room)


def index(request):
    return render(request, "chat/index.html")


def chat_room(request, room_name):
    return render(request, "chat/room.html", {"room_name": room_name})
