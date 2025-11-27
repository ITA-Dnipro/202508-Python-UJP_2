from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import StartupProjectViewSet, StartupProjectView, InternalStartupViewSet

router = DefaultRouter()
router.register(r"startup-projects", StartupProjectViewSet, basename="startupproject")
router.register(r'startup-project-search', StartupProjectView, basename='startup-search')
router.register("internal/startups", InternalStartupViewSet, basename="internal-startups")

urlpatterns = [
    path("", include(router.urls)),
]
