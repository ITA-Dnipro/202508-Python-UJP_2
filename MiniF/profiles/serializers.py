from rest_framework import serializers
from .models import StartupProfile, InvestorProfile, Industry
from projects.serializers import StartupProjectSerializer


class StartupProfileSerializer(serializers.ModelSerializer):
    """Serializer for StartupProfile model."""

    projects = StartupProjectSerializer(many=True, read_only=True)

    class Meta:
        model = StartupProfile
        fields = ['id', 'user_id', 'company_name', 'description', 'website',
                 'industry_id', 'location', 'created_at', 'updated_at', 'projects']

    def validate_company_name(self, value):
         if not value:
             raise serializers.ValidationError("Company name cannot be empty.")
         return value


class InvestorProfileSerializer(serializers.ModelSerializer):
    """Serializer for InvestorProfile model."""

    class Meta:
        model = InvestorProfile
        fields = ["id", "user_id", "investment_focus", "location", "created_at", "updated_at"]


class IndustrySerializer(serializers.ModelSerializer):
    """Serializer for IndustryProfile model."""

    class Meta:
        model = Industry
        fields = "__all__"
