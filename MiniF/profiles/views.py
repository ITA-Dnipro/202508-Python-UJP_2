from rest_framework import viewsets, filters
from .models import StartupProfile, InvestorProfile, Industry
from .serializers import StartupProfileSerializer, InvestorProfileSerializer, IndustrySerializer
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import render, get_object_or_404


class StartupProfileViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows startup profiles to be viewed or edited.
    """

    queryset = StartupProfile.objects.all()
    serializer_class = StartupProfileSerializer
    permission_classes = [IsAuthenticated]

    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["company_name", "description"]
    ordering_fields = ["created_at"]

    def get_queryset(self):
        """
        Filters that allow to filter queries.
        """

        queryset = super().get_queryset()
        params = self.request.query_params

        industry = params.get("industry")
        if industry:
            queryset = queryset.filter(industry_id__industry_name__iexact=industry)

        location = params.get("location")
        if location:
            queryset = queryset.filter(location__iexact=location)

        return queryset


def startup_list(request):
    """
    A view that returns a list of startups.
    """

    startups = StartupProfile.objects.all()
    context = {"startups": startups}
    return render(request, "startup-list.html", context)


def startup_detail(request, startup_id):
    """
    A view that returns detailed information about a chosen startup.
    """

    startup = get_object_or_404(StartupProfile, id=startup_id)
    context = {"startup": startup}
    return render(request, "startup-detail.html", context)


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
    permission_classes = [IsAuthenticated]
