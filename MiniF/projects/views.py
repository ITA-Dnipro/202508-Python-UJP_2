import logging
import pika
from django.conf import settings
from django.http import JsonResponse
from rest_framework import viewsets, filters
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from users.permissions import _get_role_from_request
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
        
        logger.info(f"Attempting to connect to RabbitMQ at {settings.RABBITMQ_HOST}")
        logger.info(f"Using exchange: {settings.RABBITMQ_EXCHANGE}, queue: {settings.RABBITMQ_QUEUE_GAMIFICATION}")
        
        connection = None
        try:
            connection = pika.BlockingConnection(
                pika.ConnectionParameters(host=settings.RABBITMQ_HOST)
            )
            logger.info("RabbitMQ connection established")
            
            channel = connection.channel()
            
            channel.exchange_declare(exchange=settings.RABBITMQ_EXCHANGE, exchange_type='topic', durable=True)
            
            routing_key = 'project.created'
            if StartupProject.objects.filter(startup_profile_id=project.startup_profile_id).count() == 1:
                routing_key = 'first.project.created'

            user_id = project.startup_profile_id.user_id.id
            role = _get_role_from_request(request)
            message_body = f'{{"user_id": {user_id}, "reference_id": "{project.id}", "role": "{role}"}}'
            logger.info(f"Message body: {message_body}")
            
            channel.basic_publish(
                exchange=settings.RABBITMQ_EXCHANGE,
                routing_key=routing_key,
                body=message_body,
                properties=pika.BasicProperties(
                    delivery_mode=pika.DeliveryMode.Persistent
                )
            )
            
            logger.info(f"Published {routing_key} event for user {user_id}, project {project.id}")
            
        except pika.exceptions.AMQPConnectionError as e:
            logger.error(f"RabbitMQ connection error: {e}")
        except pika.exceptions.AMQPChannelError as e:
            logger.error(f"RabbitMQ channel error: {e}")
        except Exception as e:
            logger.error(f"Failed to publish RabbitMQ message: {e}")

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
