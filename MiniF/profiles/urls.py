from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    StartupProfileViewSet,
    InvestorProfileViewSet,
    IndustryViewSet,
    SaveProjectView,
    SavedProjectListView,
    UnsaveProjectView,
    StartupSearchViewSet,
)
router = DefaultRouter()
router.register(r"startup-profiles", StartupProfileViewSet, basename="startupprofile")
router.register(r"investor-profiles", InvestorProfileViewSet, basename="investorprofile")
router.register(r"industries", IndustryViewSet, basename="industry")

urlpatterns = [
    path("", include(router.urls)),
    path("investor/saved-projects/", SavedProjectListView.as_view(), name="saved-projects"),
    path("investor/saved-projects/<int:saved_project_id>/unsave/", UnsaveProjectView.as_view(), name="unsave-project"),
    path("investor/save-project/<int:project_id>", SaveProjectView.as_view(), name="save-project"),
    path('search/', StartupSearchViewSet.as_view({'get': 'list'}), name='startup-search'),
]
