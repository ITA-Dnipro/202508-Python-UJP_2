from django.urls import path
from .views import NotificationListView,NotificationDetailView, NotificationDeleteView

urlpatterns = [
    path("", NotificationListView.as_view(), name="notifications-list"),
    path("<int:pk>/", NotificationDetailView.as_view(), name="notification-detail"),
    path("<int:pk>/delete/", NotificationDeleteView.as_view(), name="notification-delete"),
]
