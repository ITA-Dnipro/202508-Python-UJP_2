import logging
from django.http import JsonResponse
from rest_framework import status, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken, TokenError
from .models import UserProfile
from .serializers import (
    UserProfileSerializer,
    CustomLoginSerializer,
    PasswordResetConfirmSerializer,
)

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
        return Response(serializer.validated_data, status=status.HTTP_200_OK)


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
    POST /api/auth/confirm-token/
    body: { "token": "..." }
    """
    def get(self, request, *args, **kwargs):
        if not request.user or not request.user.is_authenticated:
            return Response({"detail": "Authentication credentials were not provided."}, status=status.HTTP_401_UNAUTHORIZED)

        # I need to return user id end role(if exist)
        return Response({"user_id": request.user.id, "role": request.auth.payload.get("role") if request.auth.payload.get("role") else None}, status=status.HTTP_200_OK)

