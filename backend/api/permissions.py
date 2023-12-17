from rest_framework import permissions
from rest_framework.permissions import IsAuthenticatedOrReadOnly


class UserIsAdmin(IsAuthenticatedOrReadOnly):

    def has_permission(self, request, view):
        return ((request.user.is_authenticated
                and request.user.is_admin)
                or request.user.is_superuser)

    def has_object_permission(self, request, view, obj):
        return ((request.user.is_authenticated
                and request.user.is_admin)
                or request.user.is_superuser)


class IsOwnerOrReadOnly(permissions.BasePermission):
    """Разрешение редактировать объект только владельцу"""

    def has_object_permission(self, request, view, obj):
        return (request.method in permissions.SAFE_METHODS
                or obj.author == request.user)
