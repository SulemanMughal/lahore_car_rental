# rental/api/serializers.py
import datetime, re
from rest_framework import serializers
from rental.models import Booking, Car


# rental/api/serializers.py
from django.utils import timezone
# from rest_framework import serializers
# from rental.models import Booking, Car
from django.contrib.auth import get_user_model

User = get_user_model()

_PLATE_RE = re.compile(r"^[A-Z0-9-]{3,16}$", re.I)

ACTIVE_BOOKING_STATUSES = {"pending", "confirmed"}  # considered blocking for overlap

class CarSerializer(serializers.ModelSerializer):
    class Meta:
        model = Car
        fields = ["id", "make", "model", "year", "plate_no", "status"]
        read_only_fields = ["id", "status"]  # status changes via a separate workflow/perm

    def validate_year(self, v):
        this_year = datetime.date.today().year
        if v < 1970 or v > this_year + 1:
            raise serializers.ValidationError("Year must be between 1970 and next year.")
        return v

    def validate_plate_no(self, v):
        v = v.strip().upper()
        if not _PLATE_RE.match(v):
            raise serializers.ValidationError("Plate must be alphanumeric/dash, 3–16 chars.")
        return v






class BookingSerializer(serializers.ModelSerializer):
    # Write: car id; Read: include a compact car summary
    car = serializers.PrimaryKeyRelatedField(queryset=Car.objects.all())
    car_summary = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Booking
        fields = ["id", "car", "car_summary", "start", "end", "status"]
        read_only_fields = ["id", "status", "car_summary"]  # status can be managed by staff later

    def get_car_summary(self, obj):
        return {
            "id": obj.car_id,
            "plate_no": obj.car.plate_no,
            "make": obj.car.make,
            "model": obj.car.model,
            "year": obj.car.year,
        }

    def validate(self, attrs):
        start = attrs.get("start")
        end = attrs.get("end")
        car = attrs.get("car")

        if start is None or end is None:
            raise serializers.ValidationError({"start": "required", "end": "required"})

        # Ensure TZ-aware and logical window
        if timezone.is_naive(start) or timezone.is_naive(end):
            raise serializers.ValidationError("start/end must be timezone-aware ISO datetimes.")
        if start >= end:
            raise serializers.ValidationError("start must be before end.")

        # Optional: disallow bookings entirely in the past
        # if end <= timezone.now():
        #     raise serializers.ValidationError("Booking window must be in the future.")

        # Car availability (simple overlap check)
        # Two ranges [a,b) & [c,d) overlap when a < d AND c < b
        qs = Booking.objects.filter(
            car=car,
            start__lt=end,
            end__gt=start,
            status__in=ACTIVE_BOOKING_STATUSES,
        )
        # On update, exclude self
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)

        if qs.exists():
            raise serializers.ValidationError(
                {"car": f"Car {car.plate_no} is already booked in the requested window."}
            )
        return attrs

    def create(self, validated):
        # Always book for the authenticated user unless staff explicitly passes a customer and is allowed
        request = self.context.get("request")
        user = request.user if request else None
        validated["customer"] = user
        return super().create(validated)
