from django.shortcuts import render
from django.http import JsonResponse
import logging

logger = logging.getLogger(__name__)


def test_user(request):
    logger.info("users/test_user endpoint called")
    try:
        response = {"status": "ok", "message": "User endpoint works"}
        logger.debug(f"Response data: {response}")
        return JsonResponse(response)
    except Exception as e:
        logger.error(f"Error in users/test_user: {e}", exc_info=True)
        return JsonResponse({"error": "Internal server error"}, status=500)


# Create your views here.
