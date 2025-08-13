from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model

User = get_user_model()

@receiver(post_save, sender=User)
def _sync_role_group_on_save(sender, instance: User, created, **kwargs):
    # Keep group membership aligned whenever users are created/updated
    try:
        instance.sync_role_group(save=False)
    except Exception:
        # Avoid breaking user creation if groups not seeded yet
        pass
