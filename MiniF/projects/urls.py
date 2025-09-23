from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import StartupProjectViewSet

router = DefaultRouter()
router.register(r"", StartupProjectViewSet, basename="startupproject")

urlpatterns = [
    path("", include(router.urls)),
]
