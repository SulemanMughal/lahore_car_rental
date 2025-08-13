# rental/signals.py
from django.db.models.signals import pre_save
from django.dispatch import receiver
from rental.models import Booking
from rental.services.booking_service import ACTIVE_BOOKING_STATUSES
from django.db.models import Q

@receiver(pre_save, sender=Booking)
def prevent_overlap_pre_save(sender, instance: Booking, **kwargs):
    # Skip if times missing
    if not instance.start or not instance.end or not instance.car_id:
        return
    qs = Booking.objects.filter(
        car=instance.car,
        start__lt=instance.end,
        end__gt=instance.start,
        status__in=ACTIVE_BOOKING_STATUSES,
    )
    if instance.pk:
        qs = qs.exclude(pk=instance.pk)
    if qs.exists():
        from django.core.exceptions import ValidationError
        raise ValidationError({"car": f"Car {instance.car.plate_no} already booked in that window."})
