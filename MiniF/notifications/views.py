from rest_framework import generics, permissions
from rest_framework import status
from .models import Notification
from .serializers import NotificationSerializer
from profiles.models import InvestorProfile
from rest_framework.response import Response

class NotificationListView(generics.ListCreateAPIView):
    """
    class to get list of investor's notifications"
    """
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        try:
            investor_profile=InvestorProfile.objects.get(user_id=self.request.user.id)
            return Notification.objects.filter(investor=investor_profile).order_by('-created_at')
        except InvestorProfile.DoesNotExist:
            return Notification.objects.none()


class NotificationDetailView(generics.RetrieveAPIView):
    """
    class to get notification details by id and make it is_read
    """
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        investor_profile = InvestorProfile.objects.get(user_id=self.request.user.id)
        return Notification.objects.filter(investor=investor_profile)

    def get_object(self):
        obj = super().get_object()

        if not obj.is_read:
            obj.is_read = True
            obj.save(update_fields=["is_read"])

        return obj

class NotificationDeleteView(generics.DestroyAPIView):
    """
    class to delete notification by id
    """
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        investor_profile = InvestorProfile.objects.get(user_id=self.request.user.id)
        return Notification.objects.filter(investor=investor_profile)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(
            {"detail": "Successfully deleted."},
            status=status.HTTP_200_OK
        )



