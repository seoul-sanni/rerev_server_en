# butlers/permissions.py
app_name = 'butlers'

from rest_framework.permissions import AllowAny, BasePermission, IsAuthenticated

from .models import ButlerRequest

class IsCIVerified(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.ci_hash)

class IsButlered(BasePermission):
    def has_object_permission(self, request, view, obj):
        try:
            butler = ButlerRequest.objects.get(car__model=obj, user=request.user, is_active=False)
            return True
        except ButlerRequest.DoesNotExist:
            return False

class IsAuthor(BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.user == request.user

class IsButlerWayPointAuthor(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        return obj.butler_request.user == request.user