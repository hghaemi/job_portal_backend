from rest_framework import permissions


class IsJobSeeker(permissions.BasePermission):
    message = "Only job seekers can perform this action."

    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and getattr(request.user, "is_jobseeker", False)
        )


class IsCompany(permissions.BasePermission):
    message = "Only companies can perform this action."

    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and getattr(request.user, "is_company", False)
        )


class IsOwner(permissions.BasePermission):
    message = "You do not have permission to modify this resource."

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        owner = getattr(obj, "user", obj)
        return owner == request.user


class IsJobOwnerCompany(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.company_id == getattr(request.user, "id", None)
