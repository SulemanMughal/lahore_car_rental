from django.contrib.auth.models import AbstractUser, Group
from django.db import models

class Roles(models.TextChoices):
    CUSTOMER = "customer", "Customer"
    FLEET_MANAGER = "fleet_manager", "Fleet Manager"
    SUPPORT = "support", "Support"
    FINANCE = "finance", "Finance"
    ADMIN = "admin", "Admin"

ROLE_TO_GROUP = {
    Roles.CUSTOMER: "customer",
    Roles.FLEET_MANAGER: "fleet_manager",
    Roles.SUPPORT: "support",
    Roles.FINANCE: "finance",
    Roles.ADMIN: "admin",   # optional: separate from superuser
}

class User(AbstractUser):
    """
    Extend AbstractUser so we keep Django admin + auth built-ins.
    We add a primary 'role' for convenience. Fine-grained access still through groups/permissions.
    """
    role = models.CharField(
        max_length=32,
        choices=Roles.choices,
        default=Roles.CUSTOMER,
        db_index=True,
    )

    phone = models.CharField(max_length=32, blank=True)
    # e.g., branch, city, etc. add as needed

    # Convenience helpers
    @property
    def is_customer(self) -> bool:
        return self.role == Roles.CUSTOMER

    @property
    def is_fleet_manager(self) -> bool:
        return self.role == Roles.FLEET_MANAGER

    @property
    def is_support(self) -> bool:
        return self.role == Roles.SUPPORT

    @property
    def is_finance(self) -> bool:
        return self.role == Roles.FINANCE

    @property
    def is_admin_role(self) -> bool:
        return self.role == Roles.ADMIN

    def sync_role_group(self, *, save: bool = True):
        """
        Ensure the user's 'role' is reflected in Group membership.
        Idempotent: removes other role groups, attaches the correct one.
        """
        target_group_name = ROLE_TO_GROUP.get(self.role)
        if not target_group_name:
            return

        target_group, _ = Group.objects.get_or_create(name=target_group_name)
        role_group_names = list(ROLE_TO_GROUP.values())

        # remove old role groups
        self.groups.remove(*Group.objects.filter(name__in=role_group_names))
        # add the target group
        self.groups.add(target_group)
        if save:
            self.save(update_fields=[])  # no field changes, but keep API uniform
