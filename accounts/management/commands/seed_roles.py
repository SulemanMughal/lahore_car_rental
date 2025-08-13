# accounts/management/commands/seed_roles.py
from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from rental.models import Car, Booking, Payment, Document

ROLE_GROUPS = ["customer", "fleet_manager", "support", "finance", "admin"]

class Command(BaseCommand):
    help = "Create role groups and attach permissions"

    def handle(self, *args, **options):
        for name in ROLE_GROUPS:
            Group.objects.get_or_create(name=name)
        self.stdout.write(self.style.SUCCESS("Groups ensured."))

        car_ct = ContentType.objects.get_for_model(Car)
        booking_ct = ContentType.objects.get_for_model(Booking)
        payment_ct = ContentType.objects.get_for_model(Payment)
        document_ct = ContentType.objects.get_for_model(Document)

        def perms(ct, codenames):
            return Permission.objects.filter(content_type=ct, codename__in=codenames)

        # default Django model perms: add/change/delete/view_<model>
        # custom perms should exist in rental.models.Meta.permissions

        customer = Group.objects.get(name="customer")
        customer.permissions.set(list({
            *perms(car_ct, ["view_car"]),
            *perms(booking_ct, ["add_booking", "view_booking", "change_booking"]),
            *perms(document_ct, ["add_document", "view_document"]),
            *perms(payment_ct, ["view_payment"]),
        }))

        fleet = Group.objects.get(name="fleet_manager")
        fleet.permissions.set(list({
            *perms(car_ct, ["view_car", "add_car", "change_car", "delete_car", "edit_status", "view_maintenance"]),
            *perms(booking_ct, ["view_booking", "change_booking"]),
            *perms(document_ct, ["view_document", "verify_document"]),
        }))

        support = Group.objects.get(name="support")
        support.permissions.set(list({
            *perms(car_ct, ["view_car"]),
            *perms(booking_ct, ["view_booking", "change_booking"]),
            *perms(payment_ct, ["view_payment"]),
            *perms(document_ct, ["view_document"]),
        }))

        finance = Group.objects.get(name="finance")
        finance.permissions.set(list({
            *perms(payment_ct, ["view_payment", "change_payment"]),
            *perms(booking_ct, ["view_booking"]),
            *perms(car_ct, ["view_car"]),
        }))

        admin_group = Group.objects.get(name="admin")
        admin_group.permissions.set(Permission.objects.all())  # full access

        self.stdout.write(self.style.SUCCESS("Permissions attached to groups."))
