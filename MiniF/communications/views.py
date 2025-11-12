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
    """Helper: extract user and role from Krakend headers."""
    try:
        user_id = request.META["HTTP_USER_ID"]
        role = request.META["HTTP_ROLE"]
        user = UserProfile.objects.get(id=user_id)
        return user, role
    except KeyError as exc:
        raise PermissionDenied("Missing authentication headers from Krakend") from exc
    except UserProfile.DoesNotExist as exc:
        raise PermissionDenied("User not found") from exc


class ConversationViewSet(viewsets.ViewSet):
    """Handle creation and listing of chat rooms (conversations)."""

    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Return all conversations related to the current user."""
        user, _ = get_user_and_role_from_headers(self.request)
        return ChatRoom.objects.filter(Q(investor=user) | Q(startup=user))

    def create(self, request):
        """Create a chat room between two users (investor-startup)."""
        try:
            current_user, role = get_user_and_role_from_headers(request)
            username = request.data.get("username")
            if not username:
                return Response(
                    {"error": "Username is required"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            try:
                other_user = UserProfile.objects.get(username=username)
            except UserProfile.DoesNotExist as exc:
                raise NotFound("User not found") from exc

            if current_user == other_user:
                return Response(
                    {"error": "Cannot chat with yourself"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            if role == "startup":
                room = (
                    ChatRoom.objects.filter(
                        investor=other_user, startup=current_user
                    ).first()
                    or ChatRoom.objects.create(
                        investor=other_user, startup=current_user
                    )
                )
            elif role == "investor":
                room = (
                    ChatRoom.objects.filter(
                        investor=current_user, startup=other_user
                    ).first()
                    or ChatRoom.objects.create(
                        investor=current_user, startup=other_user
                    )
                )
            else:
                return Response(
                    {"error": f"Invalid role: {role}"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            serializer = ChatRoomSerializer(room)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        except PermissionDenied as exc:
            return Response(
                {"error": str(exc)}, status=status.HTTP_401_UNAUTHORIZED
            )
        except Exception as exc:  # pylint: disable=broad-exception-caught
            return Response(
                {"error": str(exc)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=True, methods=["get"])
    def messages(self, request, pk=None):
        """Return all messages for a conversation."""
        try:
            room = ChatRoom.objects.get(id=pk)
            # MongoEngine uses `Message.objects` but pylint can't detect it
            messages_qs = (
                Message.objects.filter(room_id=int(room.id))
                .order_by("timestamp")  # type: ignore[attr-defined]
            )
            serializer = MessageSerializer(messages_qs, many=True)
            return Response(serializer.data)
        except ChatRoom.DoesNotExist as exc:
            raise NotFound("Conversation not found") from exc
        except Exception as exc:  # pylint: disable=broad-exception-caught
            return Response(
                {"error": str(exc)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class MessageViewSet(viewsets.ModelViewSet):
    """ViewSet for sending and retrieving messages."""

    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Return messages in rooms where user is a participant."""
        user, _ = get_user_and_role_from_headers(self.request)
        user_rooms = ChatRoom.objects.filter(Q(investor=user) | Q(startup=user))

        # Split the long query for readability and pylint compliance
        messages_query = Message.objects.filter(  # type: ignore[attr-defined]
            room__in=user_rooms
        ).order_by("-created_at")

        return messages_query

    def perform_create(self, serializer):
        """Validate and save a new message."""
        user, role = get_user_and_role_from_headers(self.request)
        room_id = self.request.data.get("room")

        if not room_id:
            raise ValidationError({"room": "Room ID is required"})

        try:
            room = ChatRoom.objects.get(id=room_id)
        except ChatRoom.DoesNotExist as exc:
            raise ValidationError({"room": "Chat room not found"}) from exc

        if user not in [room.investor, room.startup]:
            raise PermissionDenied("You are not a participant in this room.")

        if role == "startup" and room.startup != user:
            raise PermissionDenied("Startups can only send messages as the startup.")
        if role == "investor" and room.investor != user:
            raise PermissionDenied("Investors can only send messages as the investor.")

        receiver = room.startup if room.investor == user else room.investor
        serializer.save(sender=user, receiver=receiver, room=room)


def index(request):
    """Render chat login page."""
    return render(request, "chat/index.html")


def chat_room(request, room_name):
    """Render chat room page."""
    return render(request, "chat/room.html", {"room_name": room_name})
