from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsLegalReviewer(BasePermission):
    """Allow only users with profile.role == 'legal'"""

    def has_permission(self, request, view):
        user = getattr(request, 'user', None)
        if not user or not user.is_authenticated:
            return False
        profile = getattr(user, 'profile', None)
        return bool(profile and profile.role == 'legal')


class IsOwnerOrReadOnly(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        user = getattr(request, 'user', None)
        owner = getattr(obj, 'user', None) or getattr(obj, 'buyer', None)
        return bool(user and owner and user == owner)
