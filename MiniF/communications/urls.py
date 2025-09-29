from django.urls import path, include
from . import views

urlpatterns = [
    path("api/", include("communications.api_urls")),
    path("", views.index, name="index"),
    path("<str:room_name>/", views.chat_room, name="room"),
]
