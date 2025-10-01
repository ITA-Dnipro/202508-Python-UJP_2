from rest_framework.routers import DefaultRouter
from .views import StartupDocumentView

router = DefaultRouter()
router.register(r'startup-project-search', StartupDocumentView, basename='startup-search')

urlpatterns = router.urls
