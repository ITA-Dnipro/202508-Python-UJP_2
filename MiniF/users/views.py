import logging
import json
from django.conf import settings
from django.http import JsonResponse
from django.utils import timezone
from rest_framework import status, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken, TokenError
from users.permissions import _get_role_from_request
from .models import UserProfile
from .serializers import (
    UserProfileSerializer,
    CustomLoginSerializer,
    PasswordResetConfirmSerializer,
)
from core.tasks import publish_event_task

logger = logging.getLogger(__name__)



class UserProfileViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows user profiles to be viewed or edited.
    """

    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]


class CustomLoginView(APIView):
    """
    POST /api/auth/login/
    """

    def post(self, request, *args, **kwargs):
        serializer = CustomLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        email = request.data.get('email')
        user = UserProfile.objects.get(email=email)
        role = request.data.get('role')

        today = timezone.now().date()
        if user.last_login is None or user.last_login.date() < today:
            self.publish_daily_login_event(user, role)
        
        user.last_login = timezone.now()
        user.save(update_fields=['last_login'])

        return Response(serializer.validated_data, status=status.HTTP_200_OK)

    def publish_daily_login_event(self, user, role):
        routing_key = 'daily.login'
        
        message_body = json.dumps({
            "user_id": user.id,
            "reference_id": None,
            "role": role
        })
        
        publish_event_task.delay(settings.RABBITMQ_EXCHANGE, routing_key, message_body)


def test_user(request):
    logger.info("users/test_user endpoint called")
    try:
        response = {"status": "ok", "message": "User endpoint works"}
        logger.debug(f"Response data: {response}")
        return JsonResponse(response)
    except Exception as e:
        logger.error(f"Error in users/test_user: {e}", exc_info=True)
        return JsonResponse({"error": "Internal server error"}, status=500)


class CustomLogoutView(APIView):
    permission_classes = [IsAuthenticated]
    """
    POST /api/auth/logout/
    """

    def post(self, request):
        try:
            refresh_token = request.data["refresh"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({"detail": "Successfully logged out"}, status=status.HTTP_205_RESET_CONTENT)
        except KeyError:
            return Response({"detail": "Refresh token required"}, status=status.HTTP_400_BAD_REQUEST)
        except TokenError:
            return Response({"detail": "Invalid token"}, status=status.HTTP_400_BAD_REQUEST)
        
class PasswordResetConfirmAPIView(APIView):
    """
    POST /api/auth/password/reset/confirm/
    body: { "uidb64": "...", "token": "...", "new_password1": "...", "new_password2": "..." }
    """
    def post(self, request, *args, **kwargs):
        serializer = PasswordResetConfirmSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"detail": "Password changed successfully."}, status=status.HTTP_200_OK)

class ConfirmTokenView(APIView):
    """
    GET /api/auth/confirm-token/
    body: { "token": "..." }
    """

    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        return Response(
            {
                "user_id": request.user.id,
                "role": request.auth.payload.get("role") if request.auth.payload.get("role") else None
            },
            status=status.HTTP_200_OK
        )
