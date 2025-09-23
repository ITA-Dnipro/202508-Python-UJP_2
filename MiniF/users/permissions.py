from rest_framework.permissions import BasePermission
import logging

def _get_role_from_request(request):
    """
    Extract the user's role from the JWT token or from the user object.

    Returns:
        str or None: The role value ("startup", "investor") if present, otherwise None.
    """
    token = getattr(request, "auth", None)
    role = None
    if token:
        try:
            role = token.payload.get("role")
        except AttributeError:
            role = None
    if role is None and getattr(request, "user", None) and request.user.is_authenticated:
        role = getattr(request.user, "role", None)
    return role


class IsStartupRole(BasePermission):
    """
    Permission class that grants access only to users with the 'startup' role.
    """

    def has_permission(self, request, view):
        return _get_role_from_request(request) == "startup"


class IsInvestorRole(BasePermission):
    """
    Permission class that grants access only to users with the 'investor' role.
    """

    def has_permission(self, request, view):
        return _get_role_from_request(request) == "investor"

logger = logging.getLogger(__name__)


class CustomPermission(BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            logger.warning(f"Permission denied for unauthenticated user. IP: {request.META.get('REMOTE_ADDR')}")
            return False
        return True