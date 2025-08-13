# tests/conftest.py
import pytest
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from rest_framework.test import APIClient
from rental.models import Car, Booking
from django.utils import timezone

User = get_user_model()

@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def make_user(db):
    def _mk(username="u", **kwargs):
        u = User.objects.create_user(username=username, password="pass", **kwargs)
        return u
    return _mk

@pytest.fixture
def add_perms(db):
    def _add(user, codenames):
        for codename in codenames:
            p = Permission.objects.get(codename=codename)
            user.user_permissions.add(p)
        user.refresh_from_db()
        return user
    return _add

@pytest.fixture
def customer(make_user, add_perms):
    u = make_user("cust")
    # allow viewing bookings for GET /bookings/
    add_perms(u, ["view_booking"])
    return u

@pytest.fixture
def staff_writer(make_user, add_perms):
    u = make_user("writer", is_staff=True)
    # Car CRUD + booking view/add
    add_perms(u, ["add_car", "change_car", "delete_car", "view_booking", "add_booking"])
    return u

@pytest.fixture
def support_user(make_user, add_perms):
    u = make_user("support", is_staff=True)
    add_perms(u, ["view_booking"])   # support can view all bookings
    return u

@pytest.fixture
def car_factory(db):
    def _mk(**kw):
        defaults = dict(plate_no="LEA-1234", make="Toyota", model="Corolla", year=2023, status="available")
        defaults.update(kw)
        return Car.objects.create(**defaults)
    return _mk

@pytest.fixture
def booking_factory(db):
    def _mk(customer, car, start=None, end=None, status="pending"):
        now = timezone.now()
        start = start or (now + timezone.timedelta(days=1))
        end   = end or (start + timezone.timedelta(days=2))
        return Booking.objects.create(customer=customer, car=car, start=start, end=end, status=status)
    return _mk
