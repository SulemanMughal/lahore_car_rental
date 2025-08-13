# tests/test_bookings_api.py
import pytest
from django.urls import reverse
from django.utils import timezone
import datetime

pytestmark = pytest.mark.django_db

def auth(client, user):
    client.force_authenticate(user)
    return client

def test_customer_can_create_booking_when_available(api_client, customer, car_factory):
    car = car_factory()
    url = reverse("booking-list")
    start = (timezone.now() + timezone.timedelta(days=2)).isoformat()
    end   = (timezone.now() + timezone.timedelta(days=4)).isoformat()
    res = auth(api_client, customer).post(url, {"car": car.id, "start": start, "end": end}, format="json")
    assert res.status_code == 201
    body = res.json()
    assert body["success"] is True
    assert body["data"]["car"] == car.id

def test_overlapping_booking_rejected(api_client, customer, booking_factory, car_factory):
    car = car_factory()
    now = timezone.now()
    # existing booking
    booking_factory(customer=customer, car=car, start=now + timezone.timedelta(days=1), end=now + timezone.timedelta(days=3))
    # new overlaps
    url = reverse("booking-list")
    payload = {
        "car": car.id,
        "start": (now + timezone.timedelta(days=2)).isoformat(),
        "end":   (now + timezone.timedelta(days=4)).isoformat(),
    }
    res = auth(api_client, customer).post(url, payload, format="json")
    assert res.status_code == 400
    assert "already booked" in str(res.json()).lower()

def test_naive_datetimes_rejected(api_client, customer, car_factory):
    car = car_factory()
    url = reverse("booking-list")
    # naive datetimes (no tzinfo) should fail
    start = (datetime.datetime.utcnow() + datetime.timedelta(days=1)).replace(tzinfo=None).isoformat()
    end   = (datetime.datetime.utcnow() + datetime.timedelta(days=2)).replace(tzinfo=None).isoformat()
    res = auth(api_client, customer).post(url, {"car": car.id, "start": start, "end": end}, format="json")
    assert res.status_code == 400

def test_start_must_be_before_end(api_client, customer, car_factory):
    car = car_factory()
    url = reverse("booking-list")
    now = timezone.now()
    start = (now + timezone.timedelta(days=3)).isoformat()
    end   = (now + timezone.timedelta(days=2)).isoformat()
    res = auth(api_client, customer).post(url, {"car": car.id, "start": start, "end": end}, format="json")
    assert res.status_code == 400

def test_customer_lists_only_their_bookings(api_client, customer, staff_writer, booking_factory, car_factory):
    car1 = car_factory(plate_no="P1")
    car2 = car_factory(plate_no="P2")
    # customer's booking
    booking_factory(customer=customer, car=car1)
    # staff_writer booking (someone else)
    booking_factory(customer=staff_writer, car=car2)

    url = reverse("booking-list")
    res = auth(api_client, customer).get(url)
    assert res.status_code == 200
    items = res.json()["data"]["items"]
    car_ids = {i["car"] for i in items}
    assert car1.id in car_ids
    assert car2.id not in car_ids

def test_staff_sees_all_bookings(api_client, staff_writer, customer, booking_factory, car_factory, support_user):
    c1 = car_factory(plate_no="ALL-1")
    c2 = car_factory(plate_no="ALL-2")
    booking_factory(customer=customer, car=c1)
    booking_factory(customer=support_user, car=c2)

    url = reverse("booking-list")
    res = auth(api_client, staff_writer).get(url)
    assert res.status_code == 200
    items = res.json()["data"]["items"]
    assert len(items) >= 2
