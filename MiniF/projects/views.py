import logging
from django.conf import settings
from django.http import JsonResponse
from rest_framework import viewsets, filters
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ReadOnlyModelViewSet
from django_elasticsearch_dsl_drf.viewsets import DocumentViewSet
from django_elasticsearch_dsl_drf.filter_backends import (
    FilteringFilterBackend,
    OrderingFilterBackend,
    DefaultOrderingFilterBackend,
    SearchFilterBackend,
)
from .models import StartupProject
from .serializers import (
    StartupProjectSerializer,
    StartupProjectCreateUpdateSerializer,
)
from .documents import StartupDocument
from .serializers import StartupDocumentSerializer
from notifications.models import Notification, NotificationType
from profiles.models import InvestorProfile, SavedProject
from core.tasks import publish_event_task
from users.permissions import _get_role_from_request

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

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        
        project_id = response.data['id']
        project = StartupProject.objects.get(id=project_id)
        
        routing_key = 'project.created'
        if StartupProject.objects.filter(startup_profile_id=project.startup_profile_id).count() == 1:
            routing_key = 'first.project.created'

        user_id = project.startup_profile_id.user_id.id
        role = _get_role_from_request(request)
        message_body = f'{{"user_id": {user_id}, "reference_id": "{project.id}", "role": "{role}"}}'
        
        publish_event_task.delay(settings.RABBITMQ_EXCHANGE, routing_key, message_body)

        return response

    def update(self, request, *args, **kwargs):
        """
        Updating a table in the database when a change occurs in the project
        """
        response = super().update(request, *args, **kwargs)

        project = self.get_object()

        investor_ids = SavedProject.objects.filter(project=project).values_list("investor_id", flat=True)
        if not investor_ids:
            return response

        investors = InvestorProfile.objects.filter(id__in=investor_ids)

        notif_type, _ = NotificationType.objects.get_or_create(name="project_updated")

        msg = f"Проєкт «{project.title}» було оновлено."

        notifications = [
            Notification(
                investor=inv,
                startup=project.startup_profile_id,
                notification_type=notif_type,
                message=msg,
            )
            for inv in investors
        ]
        Notification.objects.bulk_create(notifications)

        return response

class InternalStartupViewSet(ReadOnlyModelViewSet):
    queryset = StartupProject.objects.all()
    serializer_class = StartupProjectSerializer