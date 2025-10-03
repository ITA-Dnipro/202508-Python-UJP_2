from django_elasticsearch_dsl_drf.serializers import DocumentSerializer
from rest_framework import serializers
from .models import StartupProject
from .documents import StartupDocument


class StartupProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = StartupProject
        fields = "__all__"

class StartupDocumentSerializer(DocumentSerializer):
    """Serializer for StartupDocument model"""

    class Meta:
        document = StartupDocument
        fields = (
            "title",
            "description",
            "status",
            "startup_name",
        )
