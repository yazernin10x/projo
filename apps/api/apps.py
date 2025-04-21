from django.apps import AppConfig


class ApiConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.api"
    verbose_name = "API"

    def ready(self):
        try:
            import apps.api.signals  # Import des signaux si nécessaire
        except ImportError:
            pass
