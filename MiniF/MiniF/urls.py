from django.contrib import admin
from django.urls import path, include
from profiles.views import startup_list, startup_detail
from drf_yasg import openapi
from drf_yasg.views import get_schema_view

schema_view = get_schema_view(
    openapi.Info(
        title="MiniF",
        default_version="v1",
        description="MiniF API documentation",
    ),
    public=True,
)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/schema/swagger/", schema_view.with_ui("swagger", cache_timeout=0), name="schema-swagger-ui"),
    path("api/users/", include("users.urls")),
    path("api/", include("users.urls")),
    path("api/profiles/", include(("profiles.urls", "profiles"), namespace="profiles")),
    path("api/projects/", include("projects.urls")),
    path("chat/", include("communications.urls")),
    path("profiles/startups/", startup_list),
    path("profiles/startups/<int:startup_id>/", startup_detail),
    path("notifications/", include("notifications.urls"))
]
