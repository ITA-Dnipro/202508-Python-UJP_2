from rest_framework import serializers
from .models import StartupProfile, InvestorProfile
from projects.serializers import StartupProjectSerializer


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


class StartupProfileCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = StartupProfile
        fields = ["company_name", "description", "website", "industry_id", "location"]

    def create(self, validated_data):
        user = self.context["request"].user
        if StartupProfile.objects.filter(user_id=user).exists():
            raise serializers.ValidationError("Startup profile already exists.")
        return StartupProfile.objects.create(user_id=user, **validated_data)


class InvestorProfileCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = InvestorProfile
        fields = ["investment_focus", "location"]

    def create(self, validated_data):
        user = self.context["request"].user
        if InvestorProfile.objects.filter(user_id=user).exists():
            raise serializers.ValidationError("Investor profile already exists.")
        return InvestorProfile.objects.create(user_id=user, **validated_data)
