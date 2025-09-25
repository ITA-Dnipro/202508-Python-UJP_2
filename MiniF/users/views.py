from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import CustomLoginSerializer
from django.shortcuts import render
from django.http import JsonResponse
import logging
from rest_framework_simplejwt.tokens import RefreshToken, TokenError

logger = logging.getLogger(__name__)


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
