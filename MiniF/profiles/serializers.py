from rest_framework import serializers
from .models import StartupProfile
from projects.serializers import StartupProjectSerializer
from .models import StartupProfile, SavedProject


class StartupProfileSerializer(serializers.ModelSerializer):
    projects = StartupProjectSerializer(many=True, read_only=True)

    class Meta:
        model = StartupProfile
        fields = [
            "id",
            "user_id",
            "company_name",
            "description",
            "website",
            "industry_id",
            "location",
            "created_at",
            "updated_at",
            "projects",
        ]

    def validate_company_name(self, value):
        if not value:
            raise serializers.ValidationError("Company name cannot be empty.")
        return value


class SavedProjectSerializer(serializers.ModelSerializer):
    project = StartupProjectSerializer(read_only=True)

    class Meta:
        model = SavedProject
        fields = ["id", "project", "created_at"]
