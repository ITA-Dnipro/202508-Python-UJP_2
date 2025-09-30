from rest_framework import serializers
from .models import StartupProfile, InvestorProfile, SavedProject
from projects.serializers import StartupProjectSerializer


class StartupProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for reading detailed startup profile data,
    including related projects.
    """

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
        """
        Ensure company name is not empty.
        """
        if not value:
            raise serializers.ValidationError("Company name cannot be empty.")
        return value


class StartupProfileCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating a new startup profile.
    Ensures that a user cannot create more than one profile.
    """

    class Meta:
        model = StartupProfile
        fields = ["company_name", "description", "website", "industry_id", "location"]

    def create(self, validated_data):
        user = self.context["request"].user
        if StartupProfile.objects.filter(user_id=user).exists():
            raise serializers.ValidationError("Startup profile already exists.")
        return StartupProfile.objects.create(user_id=user, **validated_data)


class StartupProfileUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating an existing startup profile.
    All fields are optional.
    """

    class Meta:
        model = StartupProfile
        fields = ["company_name", "description", "website", "industry_id", "location"]
        extra_kwargs = {
            "company_name": {"required": False},
            "description": {"required": False},
            "website": {"required": False},
            "industry_id": {"required": False},
            "location": {"required": False},
        }


class InvestorProfileCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating a new investor profile.
    Ensures that a user cannot create more than one profile.
    """

    class Meta:
        model = InvestorProfile
        fields = ["investment_focus", "location"]

    def create(self, validated_data):
        user = self.context["request"].user
        if InvestorProfile.objects.filter(user_id=user).exists():
            raise serializers.ValidationError("Investor profile already exists.")
        return InvestorProfile.objects.create(user_id=user, **validated_data)


class InvestorProfileUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating an existing investor profile.
    All fields are optional.
    """

    class Meta:
        model = InvestorProfile
        fields = ["investment_focus", "location"]
        extra_kwargs = {
            "investment_focus": {"required": False},
            "location": {"required": False},
        }


class SavedProjectSerializer(serializers.ModelSerializer):
    project = StartupProjectSerializer(read_only=True)

    class Meta:
        model = SavedProject
        fields = ["id", "project", "created_at"]