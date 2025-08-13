# rental/services/booking_service.py
from django.db import transaction
from django.db.models import Q
from django.utils import timezone
from rental.models import Booking, Car, Payment
from rental.payments.gateways import MockStripeGateway
from rental.validators import validate_start_end

ACTIVE_BOOKING_STATUSES = {"pending", "confirmed"}

class BookingService:
    def __init__(self, gateway=None):
        self.gateway = gateway or MockStripeGateway()

    @transaction.atomic
    def create_booking(self, *, user, car: Car, start, end, deposit_cents: int | None = None) -> Booking:
        start, end = validate_start_end(start, end)

        # Serialize same-car operations by locking the row (works across DBs)
        Car.objects.select_for_update().filter(pk=car.pk).first()

        # Re-check overlap inside the lock (two ranges overlap if a<d and c<b)
        exists = Booking.objects.select_for_update(skip_locked=True).filter(
            car=car, start__lt=end, end__gt=start, status__in=ACTIVE_BOOKING_STATUSES
        ).exists()
        if exists:
            from rest_framework import serializers
            raise serializers.ValidationError({"car": f"Car {car.plate_no} is already booked in that window."})

        # Create booking
        booking = Booking.objects.create(customer=user, car=car, start=start, end=end, status="pending")

        # Optionally schedule a deposit after commit (do not do network inside txn)
        if deposit_cents:
            def on_commit():
                res = self.gateway.create_deposit(booking=booking, amount_cents=deposit_cents, meta={"type":"deposit"})
                # Persist a Payment row either way for audit
                Payment.objects.update_or_create(
                    booking=booking,
                    defaults={"amount_cents": deposit_cents, "status": "succeeded" if res.ok else "failed"},
                )
            transaction.on_commit(on_commit)

        return booking
