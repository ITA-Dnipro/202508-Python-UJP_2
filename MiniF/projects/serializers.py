from rest_framework import serializers
from .models import StartupProject


class StartupProjectSerializer(serializers.ModelSerializer):
    """
    Serializer for StartupProject model.
    """

    class Meta:
        model = StartupProject
        fields = "__all__"
