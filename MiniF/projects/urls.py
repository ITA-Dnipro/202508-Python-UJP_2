from rest_framework.routers import DefaultRouter
from .views import StartupProjectView

router = DefaultRouter()
router.register(r'startup-project-search', StartupProjectView, basename='startup-search')

urlpatterns = router.urls
