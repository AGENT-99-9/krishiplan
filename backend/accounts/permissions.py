from rest_framework import permissions

class IsVendor(permissions.BasePermission):
    """
    Allows access only to users with the 'vendor' role.
    """
    def has_permission(self, request, view):
        return bool(request.user and request.user.get('role') == 'vendor')

class IsAdmin(permissions.BasePermission):
    """
    Allows access only to users with the 'admin' role.
    """
    def has_permission(self, request, view):
        return bool(request.user and request.user.get('role') == 'admin')

class IsVendorOrAdmin(permissions.BasePermission):
    """
    Allows access to vendors or admins.
    """
    def has_permission(self, request, view):
        return bool(request.user and request.user.get('role') in ['vendor', 'admin'])
