from rest_framework import permissions

from users.models import User


class IsAdminOrReadOnly(permissions.BasePermission):
    """Checking permission to make requests to a specific view function."""

    message = "Нет прав доступа"

    def has_permission(self, request, view):
        """Checks if the user has an admin role or the method is safe."""
        if request.method in permissions.SAFE_METHODS:
            return True
        if request.user.is_authenticated:
            return (
                request.user.role == User.ALLOWED_ROLES[0]
                or request.user.is_superuser
            )


class IsAdminModerAuthorOrReadOnly(permissions.BasePermission):
    """Checking permission to make requests to a specific view function."""
    def has_object_permission(self, request, view, obj):
        """Checking the role of a user."""
        return (
            request.method in permissions.SAFE_METHODS
            or request.user.role == User.ALLOWED_ROLES[0]
            or request.user.role == User.ALLOWED_ROLES[1]
            or obj.author == request.user
        )

    def has_permission(self, request, view):
        """Checking the action."""
        return (request.method in permissions.SAFE_METHODS
                or request.user.is_authenticated)
