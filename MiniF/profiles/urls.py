from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import StartupProfileViewSet, StartupProfileCreateView, InvestorProfileCreateView

router = DefaultRouter()
router.register(r"startup-profiles", StartupProfileViewSet, basename="startupprofile")

urlpatterns = [
    path("", include(router.urls)),
    path("startup/", StartupProfileCreateView.as_view(), name="startup-create"),
    path("investor/", InvestorProfileCreateView.as_view(), name="investor-create"),
]
