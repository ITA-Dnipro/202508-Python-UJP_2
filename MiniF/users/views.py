from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import CustomLoginSerializer
from django.shortcuts import render
from django.http import JsonResponse
import logging

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