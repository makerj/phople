from rest_framework import permissions
from rest_framework.permissions import BasePermission


class IsAuthenticated(BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated()


class IsNotAuthenticated(BasePermission):
    def has_permission(self, request, view):
        return request.user and not request.user.is_authenticated()


class IsOwnerCoupleOrReadOnly(BasePermission):
    def has_object_permission(self, request, view, datepost):
        return request.method in permissions.SAFE_METHODS or datepost.couple == request.user.couple
