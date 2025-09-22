import logging
from rest_framework.permissions import BasePermission

logger = logging.getLogger(__name__)


class CustomPermission(BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            logger.warning(f"Permission denied for unauthenticated user. IP: {request.META.get('REMOTE_ADDR')}")
            return False
        return True
