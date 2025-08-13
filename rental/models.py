# rental/models.py
from django.db import models
from django.conf import settings

from django.contrib.auth import get_user_model

User = get_user_model()

class Car(models.Model):
    STATUS = [
        ("available", "Available"),
        ("booked", "Booked"),
        ("maintenance", "Maintenance"),
        ("retired", "Retired"),
    ]
    plate_no = models.CharField(max_length=32, unique=True)
    make = models.CharField(max_length=64)
    model = models.CharField(max_length=64)
    year = models.PositiveIntegerField()
    status = models.CharField(max_length=16, choices=STATUS, default="available")

    class Meta:
        permissions = [
            ("view_maintenance", "Can view maintenance details"),
            ("edit_status", "Can change car status"),
        ]

class Booking(models.Model):
    customer = models.ForeignKey(User, on_delete=models.CASCADE)
    car = models.ForeignKey(Car, on_delete=models.PROTECT)
    start = models.DateTimeField()
    end = models.DateTimeField()
    status = models.CharField(max_length=16, default="pending")

class Payment(models.Model):
    booking = models.OneToOneField(Booking, on_delete=models.CASCADE)
    amount_cents = models.PositiveIntegerField()
    status = models.CharField(max_length=16, choices=[("succeeded","Succeeded"),("failed","Failed"),("refunded","Refunded")])

class Document(models.Model):
    customer = models.ForeignKey(User, on_delete=models.CASCADE)
    file = models.FileField(upload_to="docs/")
    doc_type = models.CharField(max_length=32)  # license, ID, etc.
    verified = models.BooleanField(default=False)

    class Meta:
        permissions = [
            ("verify_document", "Can verify customer documents"),
        ]
