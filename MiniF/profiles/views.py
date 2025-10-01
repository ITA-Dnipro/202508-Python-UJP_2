from rest_framework import viewsets, filters, generics, status
from rest_framework.generics import CreateAPIView
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import StartupProfile, InvestorProfile, SavedProject
from .serializers import (
    InvestorProfileCreateSerializer,
    StartupProfileCreateSerializer,
    StartupProfileSerializer,
    StartupProfileUpdateSerializer,
    SavedProjectSerializer
)
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.db import IntegrityError
from users.permissions import IsInvestorRole
import logging
from projects.models import StartupProject
from django.db.models import F

logger = logging.getLogger(__name__)


class StartupProfileViewSet(viewsets.ModelViewSet):
    """
    Read/Update endpoints for startup profiles.
    Supports search and ordering via query params.
    """

    queryset = StartupProfile.objects.all()
    serializer_class = StartupProfileSerializer
    permission_classes = [IsAuthenticated]

    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["company_name", "description"]
    ordering_fields = ["created_at"]

    def get_serializer_class(self):
        """
        Use an update-friendly serializer for PUT/PATCH,
        otherwise the read serializer.
        """
        if self.action in ("update", "partial_update"):
            return StartupProfileUpdateSerializer
        return StartupProfileSerializer

    def get_queryset(self):
        """
        Optionally filter by industry name and location.
        Query params:
          - industry: case-insensitive match on Industry.industry_name
          - location: case-insensitive exact match on StartupProfile.location
        """
        qs = super().get_queryset()
        params = self.request.query_params

        industry = params.get("industry")
        if industry:
            qs = qs.filter(industry_id__industry_name__iexact=industry)

        location = params.get("location")
        if location:
            qs = qs.filter(location__iexact=location)

        return qs


def startup_list(request):
    """
    Render a simple HTML list of all startup profiles.
    """
    startups = StartupProfile.objects.all()
    return render(request, "startup-list.html", {"startups": startups})


def startup_detail(request, startup_id):
    """
    Render a simple HTML detail page for a single startup profile.
    """
    startup = get_object_or_404(StartupProfile, id=startup_id)
    return render(request, "startup-detail.html", {"startup": startup})


class StartupProfileCreateView(CreateAPIView):
    """
    Create endpoint for startup profiles.
    Requires authentication; one profile per user.
    """

    serializer_class = StartupProfileCreateSerializer
    permission_classes = [IsAuthenticated]


class InvestorProfileCreateView(CreateAPIView):
    """
    Create endpoint for investor profiles.
    Requires authentication; one profile per user.
    """

    serializer_class = InvestorProfileCreateSerializer
    permission_classes = [IsAuthenticated]


class SaveProjectView(APIView):
    """
    Endpoint for saving a project for an investor.
    """
    permission_classes = [IsAuthenticated, IsInvestorRole]
    def post(self, request, project_id):
        investor = get_object_or_404(InvestorProfile, user_id=self.request.user.id)
        project = get_object_or_404(StartupProject, id=project_id)

        try:
            saved = SavedProject.objects.create(investor=investor, project=project)
            project.likes = F("likes") + 1
            project.save(update_fields=["likes"])
            project.refresh_from_db()
        except IntegrityError:
            return Response({"detail": "Project already saved"}, status=status.HTTP_400_BAD_REQUEST)

        return Response({
            "detail": "Project saved",
            "saved_project_id": saved.id,
            "investor_id": investor.id,
            "project_id": project.id
        }, status=status.HTTP_201_CREATED)


class SavedProjectListView(generics.ListAPIView):
    """
    List all projects saved by the authenticated investor.
    """
    permission_classes = [IsAuthenticated, IsInvestorRole]
    serializer_class = SavedProjectSerializer

    def get_queryset(self):
        investor = get_object_or_404(InvestorProfile, user_id=self.request.user.id)
        return SavedProject.objects.filter(investor=investor)


class UnsaveProjectView(APIView):
    """
    API endpoint to remove a saved project for an investor.
    """

    permission_classes = [IsAuthenticated, IsInvestorRole]
    def delete(self, request, saved_project_id):
        investor = get_object_or_404(InvestorProfile, user_id=self.request.user.id)

        saved = get_object_or_404(
            SavedProject,
            id=saved_project_id,
            investor=investor
        )

        if not saved:
            return Response({"detail": "Project not saved"}, status=status.HTTP_404_NOT_FOUND)

        saved.project.likes = F("likes") - 1
        saved.project.save(update_fields=["likes"])
        saved.project.refresh_from_db()
        saved.delete()

        return Response({"detail": "Project unsaved"}, status=status.HTTP_204_NO_CONTENT)
