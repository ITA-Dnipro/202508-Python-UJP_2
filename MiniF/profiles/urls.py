from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import StartupProfileViewSet, StartupProfileCreateView, InvestorProfileCreateView
from .views import StartupProfileViewSet, InvestorProfileViewSet, IndustryViewSet

router = DefaultRouter()
router.register(r"startup-profiles", StartupProfileViewSet, basename="startupprofile")
router.register(r"investor-profiles", InvestorProfileViewSet, basename="investorprofile")
router.register(r"industries", IndustryViewSet, basename="industry")

urlpatterns = [
    path("", include(router.urls)),
    path("startup/", StartupProfileCreateView.as_view(), name="startup-create"),
    path("investor/", InvestorProfileCreateView.as_view(), name="investor-create"),
]
