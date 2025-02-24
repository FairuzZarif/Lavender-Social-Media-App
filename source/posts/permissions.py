from rest_framework import permissions

class IsAuthorOrReadOnly(permissions.BasePermission):
    """Only the author can edit/delete their post, others can only read"""
    
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:  # GET, HEAD, OPTIONS
            return True
        return obj.author == request.user
