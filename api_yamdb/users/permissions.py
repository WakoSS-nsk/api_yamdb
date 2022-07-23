from rest_framework import permissions


class RoleBasedPermission(permissions.BasePermission):
    """Checking permission to make requests to a specific view function."""
    def has_permission(self, request, view):
        """
        User role values should be listed in `allowed_roles` as a list or
        tuple.
        """
        if request.user.is_authenticated and request.user.is_active:
            return (
                request.user.role in view.allowed_roles
                or request.user.is_superuser
            )
