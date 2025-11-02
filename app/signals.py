from django.conf import settings
from django.apps import apps
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import UserProfile


# Resolve the User model after apps are ready via apps.get_model in AppConfig.ready()
app_label, model_name = settings.AUTH_USER_MODEL.split('.')
User = apps.get_model(app_label, model_name)


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Automatically create a UserProfile for each new user (default role = buyer)."""
    if created:
        UserProfile.objects.get_or_create(user=instance, defaults={"role": UserProfile.Role.BUYER})
