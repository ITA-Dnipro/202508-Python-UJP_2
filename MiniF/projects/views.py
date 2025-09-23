from django.shortcuts import render
from rest_framework import viewsets
from .models import StartupProject
from .serializers import StartupProjectSerializer
from rest_framework.permissions import IsAuthenticated
from django.http import JsonResponse
import logging

logger = logging.getLogger(__name__)

def test_project(request):
    logger.info("projects/test_project endpoint called")
    try:
        response = {"status": "ok", "message": "Projects endpoint works"}
        logger.debug(f"Response data: {response}")
        return JsonResponse(response)
    except Exception as e:
        logger.error(f"Error in projects/test_project: {e}", exc_info=True)
        return JsonResponse({"error": "Internal server error"}, status=500)


class StartupProjectViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows startup projects to be viewed or edited.
    """

    queryset = StartupProject.objects.all()
    serializer_class = StartupProjectSerializer
    permission_classes = [IsAuthenticated]
