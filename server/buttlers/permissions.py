# subscriptions/permissions.py
app_name = 'subscriptions'

from rest_framework.permissions import AllowAny, BasePermission, IsAuthenticated

from .models import ButtlerRequest

class IsCIVerified(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.ci_hash)

class IsButtled(BasePermission):
    def has_object_permission(self, request, view, obj):
        try:
            buttler = ButtlerRequest.objects.get(car__model=obj, user=request.user, is_active=False)
            return True
        except ButtlerRequest.DoesNotExist:
            return False

class IsAuthor(BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.user == request.user