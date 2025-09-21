from rest_framework import viewsets, filters
from rest_framework.permissions import IsAuthenticated
from rest_framework.generics import CreateAPIView
from django.shortcuts import render, get_object_or_404

from .models import StartupProfile
from .serializers import (
    StartupProfileSerializer,
    StartupProfileCreateSerializer,
    InvestorProfileCreateSerializer,
)


class StartupProfileViewSet(viewsets.ModelViewSet):
    queryset = StartupProfile.objects.all()
    serializer_class = StartupProfileSerializer
    permission_classes = [IsAuthenticated]

    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["company_name", "description"]
    ordering_fields = ["created_at"]

    def get_queryset(self):
        qs = super().get_queryset()
        p = self.request.query_params
        industry = p.get("industry")
        if industry:
            qs = qs.filter(industry_id__industry_name__iexact=industry)
        location = p.get("location")
        if location:
            qs = qs.filter(location__iexact=location)
        return qs


def startup_list(request):
    startups = StartupProfile.objects.all()
    return render(request, "startup-list.html", {"startups": startups})


def startup_detail(request, startup_id):
    startup = get_object_or_404(StartupProfile, id=startup_id)
    return render(request, "startup-detail.html", {"startup": startup})


class StartupProfileCreateView(CreateAPIView):
    serializer_class = StartupProfileCreateSerializer
    permission_classes = [IsAuthenticated]


class InvestorProfileCreateView(CreateAPIView):
    serializer_class = InvestorProfileCreateSerializer
    permission_classes = [IsAuthenticated]
