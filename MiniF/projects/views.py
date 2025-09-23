from django.shortcuts import render
from rest_framework import viewsets
from .models import StartupProject
from .serializers import StartupProjectSerializer
from rest_framework.permissions import IsAuthenticated


class StartupProjectViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows startup projects to be viewed or edited.
    """

    queryset = StartupProject.objects.all()
    serializer_class = StartupProjectSerializer
    permission_classes = [IsAuthenticated]
