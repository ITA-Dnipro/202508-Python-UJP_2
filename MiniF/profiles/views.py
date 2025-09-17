from django.shortcuts import render
from django.http import JsonResponse
import logging

logger = logging.getLogger(__name__)

def test_profile(request):
    logger.info("profiles/test_profile endpoint called")
    try:
        response = {"status": "ok", "message": "Profile endpoint works"}
        logger.debug(f"Response data: {response}")
        return JsonResponse(response)
    except Exception as e:
        logger.error(f"Error in profiles/test_profile: {e}", exc_info=True)
        return JsonResponse({"error": "Internal server error"}, status=500)

# Create your views here.
