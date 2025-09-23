from rest_framework import viewsets, filters
from rest_framework.generics import CreateAPIView
from .models import StartupProfile, InvestorProfile, Industry
from .serializers import (
    InvestorProfileCreateSerializer,
    StartupProfileCreateSerializer,
    StartupProfileSerializer,
    StartupProfileUpdateSerializer,
    InvestorProfileSerializer, 
    IndustrySerializer,
)
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import render, get_object_or_404
import logging

logger = logging.getLogger(__name__)


class StartupProfileViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows startup profiles to be viewed or edited.
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
    context = {"startup": startup}
    return render(request, "startup-detail.html", {"startup": startup})

class InvestorProfileViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows investor profiles to be viewed or edited.
    """

    queryset = InvestorProfile.objects.all()
    serializer_class = InvestorProfileSerializer
    permission_classes = [IsAuthenticated]


class IndustryViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows industries to be viewed or edited.
    """

    queryset = Industry.objects.all()
    serializer_class = IndustrySerializer

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
