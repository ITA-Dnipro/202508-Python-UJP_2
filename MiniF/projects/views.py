from django.shortcuts import render
from rest_framework import viewsets, filters
from .models import StartupProject
from .serializers import StartupProjectSerializer
from rest_framework.permissions import IsAuthenticated
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
import logging

from .models import StartupProject
from .serializers import StartupProjectSerializer, StartupProjectCreateUpdateSerializer

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
    API endpoint for managing startup projects.
    Supports search and ordering.
    """

    queryset = StartupProject.objects.all()
    serializer_class = StartupProjectSerializer
    permission_classes = [IsAuthenticated]

    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["title", "description", "status"]
    ordering_fields = ["created_at", "likes"]
    
    def get_serializer_class(self):
        """
        Use an update-friendly serializer for PUT/PATCH,
        otherwise the read serializer.
        """
        if self.action in ("create", "update", "partial_update"):
            return StartupProjectCreateUpdateSerializer
        return StartupProjectSerializer


    def get_queryset(self):
        """
        Optionally filter projects by startup_profile_id.
        Example: /api/projects/startup-projects/?startup_id=3
        """
        qs = super().get_queryset()
        startup_id = self.request.query_params.get("startup_id")
        if startup_id:
            qs = qs.filter(startup_profile_id=startup_id)
        return qs