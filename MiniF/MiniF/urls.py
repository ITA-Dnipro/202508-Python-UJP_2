from django.contrib import admin
from django.urls import path, include
from core.views import health

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include("users.urls")),
    path("api/profiles/", include("profiles.urls")),
    path("chat/", include("communications.urls")),
    path("api/profiles/", include("profiles.urls")),
]
