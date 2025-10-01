from django.contrib import admin
from django.urls import path, include
from profiles.views import startup_list, startup_detail

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include("users.urls")),
    path("api/profiles/", include("profiles.urls")),
    path("api/projects/", include("projects.urls")),
    path("chat/", include("communications.urls")),
    path("profiles/startups/", startup_list, name="startup_list"),
    path("profiles/startups/<int:startup_id>/", startup_detail, name="startup_detail"),
]
