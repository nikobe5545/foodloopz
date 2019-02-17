from rest_framework.permissions import BasePermission
from rest_framework.request import Request


class IsNotAuthenticated(BasePermission):
    """
    Allows access only to non authenticated users.
    """

    def has_permission(self, request: Request, view):
        return request.user and not request.user.is_authenticated
