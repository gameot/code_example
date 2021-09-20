from rest_framework.permissions import BasePermission
from rest_framework.request import Request
from rest_framework.viewsets import ModelViewSet

from house.models import House
from user.models import User


class IsSelf(BasePermission):
    def has_object_permission(self, request: Request, view: ModelViewSet, instance) -> bool:
        is_self: bool = False
        if isinstance(instance, User):
            is_self = instance == request.user
        return is_self


class IsAuthenticatedOrCreate(BasePermission):
    def has_permission(self, request: Request, view: ModelViewSet) -> bool:
        is_authenticated = bool(request.user and request.user.is_authenticated)
        is_create = view.action in ['create', ]
        if is_authenticated and not is_create:
            return True
        elif not is_authenticated and is_create:
            return True
        return False


class IsOwner(BasePermission):
    def has_object_permission(self, request: Request, view: ModelViewSet, instance: House) -> bool:
        return instance.operator == request.user
