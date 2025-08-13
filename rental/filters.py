# rental/filters.py
import django_filters
from rental.models import Booking

class BookingFilter(django_filters.FilterSet):
    from_ = django_filters.IsoDateTimeFilter(field_name="start", lookup_expr="gte", label="from")
    to = django_filters.IsoDateTimeFilter(field_name="end", lookup_expr="lte")
    status = django_filters.CharFilter(field_name="status", lookup_expr="iexact")
    car = django_filters.NumberFilter(field_name="car_id")

    class Meta:
        model = Booking
        fields = ["from_", "to", "status", "car"]
