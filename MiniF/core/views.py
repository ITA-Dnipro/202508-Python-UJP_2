from django.shortcuts import render
from django.http import JsonResponse
import logging

logger = logging.getLogger(__name__)

def health(request):
    logger.info("Health check endpoint was called")
    print("LOGGER LOADED:", logger)
    try:
        response = {"status": "ok", "app": "MiniF"}
        logger.debug(f"Response data: {response}")
        return JsonResponse(response)
    except Exception as e:
        logger.error(f"Error in health endpoint: {e}", exc_info=True)
        return JsonResponse({"error": "Internal server error"}, status=500)
