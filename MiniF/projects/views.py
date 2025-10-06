from rest_framework import viewsets
from .models import StartupProject
from .serializers import StartupProjectSerializer
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import render
from django.http import JsonResponse
import logging
from django_elasticsearch_dsl_drf.viewsets import DocumentViewSet
from django_elasticsearch_dsl_drf.filter_backends import (
    FilteringFilterBackend,
    OrderingFilterBackend,
    DefaultOrderingFilterBackend,
    SearchFilterBackend,
)
from .documents import StartupDocument
from .serializers import StartupDocumentSerializer

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

      
class StartupProjectView(DocumentViewSet):
    """Search endpoint for startup projects."""

    document = StartupDocument
    serializer_class = StartupDocumentSerializer
    lookup_field = 'id'
    
    filter_backends = [
        FilteringFilterBackend,
        OrderingFilterBackend,
        DefaultOrderingFilterBackend,
        SearchFilterBackend,
    ]
    search_fields = (
        'startup_name',
        'title',
        'description',
    )
    filter_fields = {
        'status': 'status',
        'startup_name': 'startup_name',
    }
    ordering_fields = {
        'startup_name': 'startup_name.raw',
        'title': 'title',
    }
    ordering = ('startup_name.raw',)


class StartupProjectViewSet(viewsets.ModelViewSet):
    queryset = StartupProject.objects.all()
    serializer_class = StartupProjectSerializer
    permission_classes = [IsAuthenticated]
  
