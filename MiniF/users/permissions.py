from rest_framework.permissions import BasePermission


class IsStartupRole(BasePermission):
    def has_permission(self, request, view):
        token = getattr(request, "auth", None)
        role = getattr(token, "payload", {}).get("role") if token else None
        # Pylance підсвічує? fallback:
        if role is None and hasattr(request.user, "is_authenticated") and request.user.is_authenticated:
            role = getattr(request.user, "role", None)
        return role == "startup"


class IsInvestorRole(BasePermission):
    def has_permission(self, request, view):
        token = getattr(request, "auth", None)
        role = getattr(token, "payload", {}).get("role") if token else None
        if role is None and hasattr(request.user, "is_authenticated") and request.user.is_authenticated:
            role = getattr(request.user, "role", None)
        return role == "investor"
