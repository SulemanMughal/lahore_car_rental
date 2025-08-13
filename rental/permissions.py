# rental/api/permissions.py
from rest_framework.permissions import BasePermission, SAFE_METHODS

class CarPermission(BasePermission):
    """
    - GET (list): any authenticated user (results are filtered in queryset).
    - POST: requires rental.add_car
    - PUT/PATCH: requires rental.change_car
    - DELETE: requires rental.delete_car
    """
    def has_permission(self, request, view):
        u = request.user
        if not u or not u.is_authenticated:
            return False
        if request.method in SAFE_METHODS:
            return True
        if request.method == "POST":
            return u.has_perm("rental.add_car")
        if request.method in ("PUT", "PATCH"):
            return u.has_perm("rental.change_car")
        if request.method == "DELETE":
            return u.has_perm("rental.delete_car")
        return False

    def has_object_permission(self, request, view, obj):
        # same as global; add object-level constraints if needed later
        return self.has_permission(request, view)




class BookingPermission(BasePermission):
    def has_permission(self, request, view):
        u = request.user
        if not u or not u.is_authenticated:
            return False
        if request.method in SAFE_METHODS:
            return u.has_perm("rental.view_booking")
        if request.method == "POST":
            return u.has_perm("rental.add_booking")
        return False  # only list/create per spec

    def has_object_permission(self, request, view, obj):
        # For future retrieve/update, customers should only access their own objects
        if request.method in SAFE_METHODS:
            return request.user.has_perm("rental.view_booking")
        return request.user.has_perm("rental.add_booking")
