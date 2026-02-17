from rest_framework.permissions import BasePermission


class IsAdmin(BasePermission):
    """
    Permission check for admin users.
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and (
            request.user.role == 'admin' or request.user.is_superuser
        )


class IsOwnerOrAdmin(BasePermission):
    """
    Permission check: object owner or admin.
    """
    def has_object_permission(self, request, view, obj):
        if request.user.role == 'admin' or request.user.is_superuser:
            return True
        return obj == request.user