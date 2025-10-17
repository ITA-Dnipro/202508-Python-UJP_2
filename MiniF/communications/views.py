from django.db.models import Q
from django.shortcuts import render

from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.exceptions import NotFound, PermissionDenied, ValidationError
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication

from users.models import UserProfile
from users.permissions import IsStartupRole, IsInvestorRole, _get_role_from_request

from .models import ChatRoom, Message
from .serializers import ChatRoomSerializer, MessageSerializer



class ConversationViewSet(viewsets.ViewSet):
    """
    ViewSet for managing chat conversations between users.
    Requires JWT authentication for all endpoints.
    """

    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Return chat rooms where the current user is either investor or startup"""
        if not self.request.user.is_authenticated:
            raise PermissionDenied("Authentication credentials were not provided.")

        return ChatRoom.objects.filter(Q(investor=self.request.user) | Q(startup=self.request.user))

    def get_permissions(self):
        """Override get_permissions to allow create action for all authenticated users"""
        if self.action in ["create"]:
            return [permissions.IsAuthenticated()]
        return [IsStartupRole() | IsInvestorRole()]

    def create(self, request):  # pylint: disable=too-many-return-statements
        """
        Create a new chat room or return existing one.

        Request format:
        {
            "username": "username_of_other_user"
        }
        """
        try:
            # Check authentication first
            if not request.user or not request.user.is_authenticated:
                return Response(
                    {"error": "Authentication credentials were not provided."}, status=status.HTTP_401_UNAUTHORIZED
                )

            username = request.data.get("username")

            if not username:
                return Response({"error": "Username of the other user is required"}, status=status.HTTP_400_BAD_REQUEST)

            # Get the current user
            current_user = request.user
            role = request.auth.payload.get("role") if request.auth else None
            if not role:
                return Response(
                    {"error": "Role not found in token or token not provided."}, status=status.HTTP_400_BAD_REQUEST
                )

            # Find the other user by username
            try:
                other_user = UserProfile.objects.get(username=username)
            except UserProfile.DoesNotExist:
                return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
            except Exception as exc:
                raise RuntimeError("Unexpected error while creating chat") from exc

            # Check if trying to create a chat with self
            if current_user == other_user:
                return Response(
                    {"error": "Cannot create a conversation with yourself"}, status=status.HTTP_400_BAD_REQUEST
                )

            if role == "startup":
                room = ChatRoom.objects.filter(
                    Q(investor=other_user) & Q(startup=current_user)
                ).first() or ChatRoom.objects.create(investor=other_user, startup=current_user)
            elif role == "investor":
                room = ChatRoom.objects.filter(
                    Q(investor=current_user) & Q(startup=other_user)
                ).first() or ChatRoom.objects.create(investor=current_user, startup=other_user)
            else:
                return Response({"error": "Role not recognized or not provided."}, status=status.HTTP_400_BAD_REQUEST)

            serializer = ChatRoomSerializer(room)
            return Response(serializer.data, status=status.HTTP_201_CREATED if not room.pk else status.HTTP_200_OK)

        except Exception as exc:  # pylint: disable=broad-exception-caught
            return Response({"error": str(exc)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=True, methods=["get"])
    def messages(self, request, pk=None):
        """List all messages in a specific conversation"""
        try:
            messages = Message.objects.filter(room_id=pk).order_by("timestamp")  # pylint: disable=no-member
            serializer = MessageSerializer(messages, many=True)
            return Response(serializer.data)
        except ChatRoom.DoesNotExist as exc:
            raise NotFound("Conversation not found") from exc


class MessageViewSet(viewsets.ModelViewSet):  # pylint: disable=too-many-ancestors
    """
    ViewSet for managing messages in chat rooms.
    Requires JWT authentication for all endpoints.
    """

    serializer_class = MessageSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Only return messages from rooms where the user is a participant."""
        return Message.objects.filter(  # pylint: disable=no-member
            room__in=ChatRoom.objects.filter(Q(investor=self.request.user) | Q(startup=self.request.user))
        ).order_by("-created_at")

    def get_permissions(self):
        """Override get_permissions to allow create action for all authenticated users"""
        if self.action in ["create", "perform_create"]:
            return [IsStartupRole() | IsInvestorRole()]  # Лише стартапи або інвестори
        return [permissions.IsAuthenticated()]  # Для інших дій

    def perform_create(self, serializer):
        room_id = self.request.data.get("room")
        if not room_id:
            raise ValidationError({"room": "Room ID is required"})

        try:
            room = ChatRoom.objects.get(id=room_id)
            if self.request.user not in [room.investor, room.startup]:
                raise PermissionDenied("You are not a participant in this chat room.")

            role = _get_role_from_request(self.request)
            if role == "startup" and room.startup != self.request.user:
                raise PermissionDenied("Startups can only send messages as the startup in the room.")
            if role == "investor" and room.investor != self.request.user:
                raise PermissionDenied("Investors can only send messages as the investor in the room.")

            receiver = room.startup if room.investor == self.request.user else room.investor
            serializer.save(sender=self.request.user, receiver=receiver, room=room)

        except ChatRoom.DoesNotExist as exc:
            raise ValidationError({"room": "Chat room not found"}) from exc


def index(request):
    """Render the chat index page."""
    return render(request, "chat/index.html")


def chat_room(request, room_name):
    """Render the chat room page with the given room name."""
    return render(request, "chat/room.html", {"room_name": room_name})
