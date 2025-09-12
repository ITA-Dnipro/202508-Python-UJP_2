from rest_framework import viewsets
from .models import StartupProfile
from .serializers import StartupProfileSerializer
from rest_framework.permissions import IsAuthenticated

class StartupProfileViewSet(viewsets.ModelViewSet):
    queryset = StartupProfile.objects.all()
    serializer_class = StartupProfileSerializer
    permission_classes = [IsAuthenticated]