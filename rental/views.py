# rental/api/views.py
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from django.db import transaction
from rest_framework.viewsets import GenericViewSet
from rest_framework.mixins import CreateModelMixin, ListModelMixin

from rental.models import Car, Booking
from .serializers import CarSerializer, BookingSerializer
from .permissions import CarPermission, BookingPermission
from rest_framework import serializers

from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiResponse

from rental.filters import BookingFilter
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter

from rental.services.booking_service import BookingService




ACTIVE_BOOKING_STATUSES = {"pending", "confirmed"}  # considered blocking for overlap


def envelope(request, *, data=None, error=None, code=status.HTTP_200_OK):
    return Response(
        {"success": error is None, "data": (data if error is None else None), "error": error,
         "trace_id": getattr(request, "request_id", None)},
        status=code,
    )

class VehicleViewSet(ModelViewSet):
    """
    Routes:
      POST   /vehicles/         -> Add a car
      PUT    /vehicles/{id}/    -> Update a car
      DELETE /vehicles/{id}/    -> Delete a car
      GET    /vehicles/         -> List user's vehicles (or all for fleet/admin)
    """
    serializer_class = CarSerializer
    permission_classes = [IsAuthenticated, CarPermission]
    http_method_names = ["get", "post", "put", "delete", "head", "options"]

    def get_queryset(self):
        # Handle schema generation
        if getattr(self, 'swagger_fake_view', False):
            return Car.objects.none()
            
        u = self.request.user

        # writers (fleet/admin) see all cars
        is_writer = (
            u.has_perm("rental.add_car") or
            u.has_perm("rental.change_car") or
            u.has_perm("rental.delete_car")
        )

        if is_writer:
            qs = Car.objects.all()
        else:
            # "user's vehicles" = cars this user has booked (any time)
            # reverse query name is 'booking' by default
            qs = Car.objects.filter(booking__customer=u).distinct()

            # Optional: limit to current/future bookings only
            active = self.request.query_params.get("active")
            if active and active.lower() in ("1", "true", "yes"):
                now = timezone.now()
                qs = qs.filter(booking__start__lte=now, booking__end__gte=now).distinct()

        # Optional filters
        make = self.request.query_params.get("make")
        model = self.request.query_params.get("model")
        if make:
            qs = qs.filter(make__icontains=make)
        if model:
            qs = qs.filter(model__icontains=model)

        return qs

    # enveloped responses
    def list(self, request, *a, **kw):
        qs = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(qs)
        ser = self.get_serializer(page or qs, many=True)
        if page is not None:
            # If you want the same envelope for paginated lists, swap DRF paginator to a custom one later
            return self.get_paginated_response(ser.data)
        return envelope(request, data={"items": ser.data})

    def create(self, request, *a, **kw):
        s = self.get_serializer(data=request.data)
        s.is_valid(raise_exception=True)
        s.save()
        return envelope(request, data=s.data, code=status.HTTP_201_CREATED)

    def update(self, request, *a, **kw):
        car = self.get_object()
        s = self.get_serializer(car, data=request.data, partial=False)
        s.is_valid(raise_exception=True)
        s.save()
        return envelope(request, data=s.data)

    def destroy(self, request, *a, **kw):
        car = self.get_object()
        car.delete()
        return envelope(request, data={"deleted": True}, code=status.HTTP_200_OK)







def envelope(request, *, data=None, error=None, code=status.HTTP_200_OK):
    return Response(
        {"success": error is None, "data": (data if error is None else None), "error": error,
         "trace_id": getattr(request, "request_id", None)},
        status=code,
    )



@extend_schema_view(
    list=extend_schema(tags=["Bookings"], responses={200: OpenApiResponse(description="User bookings (staff: all)")}),
    create=extend_schema(tags=["Bookings"], responses={201: OpenApiResponse(description="Booking created")}),
)
class BookingViewSet(CreateModelMixin, ListModelMixin, GenericViewSet):
    """
    POST /bookings/ -> Book a vehicle
    GET  /bookings/ -> List bookings for current user (staff sees all)
    """
    serializer_class = BookingSerializer
    permission_classes = [IsAuthenticated, BookingPermission]
    http_method_names = ["get", "post", "head", "options"]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_class = BookingFilter
    ordering = ["-start"]

    def get_queryset(self):
        # Handle schema generation
        if getattr(self, 'swagger_fake_view', False):
            return Booking.objects.none()
            
        u = self.request.user
        role = (getattr(u, "role", "") or "").lower()
        qs = Booking.objects.select_related("car", "customer")
        if role in {"admin", "fleet_manager", "support", "finance"}:
            return qs.order_by("-start")
        return qs.filter(customer=u).order_by("-start")

    # enveloped responses
    def list(self, request, *a, **kw):
        qs = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(qs)
        ser = self.get_serializer(page or qs, many=True)
        if page is not None:
            return self.get_paginated_response(ser.data)
        return envelope(request, data={"items": ser.data})

    @transaction.atomic
    def create(self, request, *a, **kw):
        s = self.get_serializer(data=request.data)
        s.is_valid(raise_exception=True)

        car = s.validated_data["car"]
        start = s.validated_data["start"]
        end   = s.validated_data["end"]

        # Example: $100 deposit (10000 cents). Make it configurable.
        booking = BookingService().create_booking(
            user=request.user, car=car, start=start, end=end, deposit_cents=10000
        )
        out = BookingSerializer(booking).data
        return envelope(request, data=out, code=status.HTTP_201_CREATED)
