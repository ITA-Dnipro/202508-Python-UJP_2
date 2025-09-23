from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import StartupProfileViewSet, SaveProjectView, SavedProjectListView, UnsaveProjectView

router = DefaultRouter()
router.register(r"startup-profiles", StartupProfileViewSet, basename="startupprofile")

urlpatterns = [
    path("", include(router.urls)),
    path("investor/saved-projects/", SavedProjectListView.as_view(), name="saved-projects"),
    path("investor/saved-projects/unsave/", UnsaveProjectView.as_view(), name="unsave-project"),
    path("investor/save-project/", SaveProjectView.as_view(), name="save-project"),
]
