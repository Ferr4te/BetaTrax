from rest_framework.permissions import BasePermission

# Use to check if the user is authenticated and has the appropriate role for accessing views
# Always return False for unauthenticated users
# Always return True for superuser

# For viewset PBI:
# Adding permission_classes=[IsAuthenticated, IsProductOwner] in the viewset action()

# For function PBI (should be):
# if not (request.user.is_superuser or hasattr(request.user, 'productowner')):
#    raise PermissionDenied("You do not have permission to assign defects.")

# Since the admin site only allows superusers to log in
# so if you want to check is the permission working
# you have to create some users with role when you login the superuser account
# then grant the user staff status in the admin site to allow them to log in
# after that you can see the permission is working when you try to access the view that require permission

class IsProductOwner(BasePermission):
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        if request.user.is_superuser:
            return True
        return hasattr(request.user, 'productowner')

class IsDeveloper(BasePermission):
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        if request.user.is_superuser:
            return True
        return hasattr(request.user, 'developer')

class IsBetaTester(BasePermission):
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        if request.user.is_superuser:
            return True
        return hasattr(request.user, 'betatester')