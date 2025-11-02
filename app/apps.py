from django.apps import AppConfig


class AppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'app'

    def ready(self):
        # Import signal handlers to auto-create UserProfile on user creation
        # Import occurs only once when app registry is ready
        from . import signals  # noqa: F401
