from rest_framework import serializers
from .models import StartupProject

class StartupProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = StartupProject
        fields = '__all__'
