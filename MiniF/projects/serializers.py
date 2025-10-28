from django_elasticsearch_dsl_drf.serializers import DocumentSerializer
from rest_framework import serializers
from .models import StartupProject
from .documents import StartupDocument

class StartupProjectSerializer(serializers.ModelSerializer):
    startup_company = serializers.CharField(source="startup_profile_id.company_name", read_only=True)

    class Meta:
        model = StartupProject
        fields = [
            "id",
            "startup_profile_id",
            "startup_company",
            "title",
            "description",
            "status",
            "likes",
            "created_at",
            "updated_at",
        ]

class StartupProjectCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = StartupProject
        fields = ["startup_profile_id", "title", "description", "status"]


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

        ref_name = "projects"

