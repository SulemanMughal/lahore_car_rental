# rental/api/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import VehicleViewSet, BookingViewSet

router = DefaultRouter()
router.register("vehicles", VehicleViewSet, basename="vehicle")
router.register("bookings", BookingViewSet, basename="booking")

urlpatterns = [path("", include(router.urls))]

