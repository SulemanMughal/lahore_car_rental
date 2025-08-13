# tests/test_vehicles_api.py
import pytest
from django.urls import reverse
from django.utils import timezone

pytestmark = pytest.mark.django_db

def auth(client, user):
    client.force_authenticate(user)
    return client

def test_writer_can_create_car(api_client, staff_writer):
    url = reverse("vehicle-list")
    payload = {"make": "Honda", "model": "Civic", "year": 2024, "plate_no": "LEB-7788"}
    res = auth(api_client, staff_writer).post(url, payload, format="json")
    assert res.status_code == 201
    body = res.json()
    assert body["success"] is True
    assert body["data"]["plate_no"] == "LEB-7788"

def test_customer_cannot_create_car(api_client, customer):
    url = reverse("vehicle-list")
    payload = {"make": "Honda", "model": "Civic", "year": 2024, "plate_no": "LEB-7788"}
    res = auth(api_client, customer).post(url, payload, format="json")
    assert res.status_code in (403, 401)  # CarPermission requires add_car

def test_list_vehicles_customer_sees_only_booked(api_client, customer, staff_writer, car_factory, booking_factory):
    car1 = car_factory(plate_no="LEA-0001")
    car2 = car_factory(plate_no="LEA-0002")
    # Customer books car1 only
    booking_factory(customer=customer, car=car1)

    url = reverse("vehicle-list")
    res = auth(api_client, customer).get(url)
    assert res.status_code == 200
    items = res.json()["data"]["items"]
    plates = {i["plate_no"] for i in items}
    assert "LEA-0001" in plates
    assert "LEA-0002" not in plates  # not booked by this user

def test_writer_lists_all_vehicles(api_client, staff_writer, car_factory):
    car_factory(plate_no="AAA-1111")
    car_factory(plate_no="BBB-2222")
    url = reverse("vehicle-list")
    res = auth(api_client, staff_writer).get(url)
    assert res.status_code == 200
    items = res.json()["data"]["items"]
    assert {i["plate_no"] for i in items} >= {"AAA-1111", "BBB-2222"}

def test_update_requires_change_perm(api_client, customer, staff_writer, car_factory):
    car = car_factory(plate_no="UPD-9999")
    url = reverse("vehicle-detail", args=[car.id])
    # customer cannot
    res1 = auth(api_client, customer).put(url, {"make":"X","model":"Y","year":2024,"plate_no":"UPD-9999"}, format="json")
    assert res1.status_code in (403, 401)
    # writer can
    res2 = auth(api_client, staff_writer).put(url, {"make":"X","model":"Y","year":2024,"plate_no":"UPD-9999"}, format="json")
    assert res2.status_code == 200
    assert res2.json()["data"]["make"] == "X"

def test_delete_requires_delete_perm(api_client, customer, staff_writer, car_factory):
    car = car_factory(plate_no="DEL-123")
    url = reverse("vehicle-detail", args=[car.id])
    assert auth(api_client, customer).delete(url).status_code in (403, 401)
    assert auth(api_client, staff_writer).delete(url).status_code == 200

def test_plate_and_year_validation(api_client, staff_writer):
    url = reverse("vehicle-list")
    bad_plate = {"make":"T","model":"M","year":2024,"plate_no":"???"}
    res1 = auth(api_client, staff_writer).post(url, bad_plate, format="json")
    assert res1.status_code == 400
    too_old = {"make":"T","model":"M","year":1900,"plate_no":"OK-123"}
    res2 = auth(api_client, staff_writer).post(url, too_old, format="json")
    assert res2.status_code == 400
