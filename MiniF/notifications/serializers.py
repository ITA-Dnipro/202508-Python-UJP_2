from rest_framework import serializers
from .models import Notification
from profiles.models import InvestorProfile

class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = "__all__"
