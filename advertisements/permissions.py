from rest_framework.permissions import BasePermission


class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and (
            request.user.role == 'admin' or request.user.is_superuser
        )


class IsAdvertisementOwner(BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.owner == request.user


class IsAdvertisementOwnerOrAdmin(BasePermission):
    def has_object_permission(self, request, view, obj):
        return (
            obj.owner == request.user or
            request.user.role == 'admin' or
            request.user.is_superuser
        )