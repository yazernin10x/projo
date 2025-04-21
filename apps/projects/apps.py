from django.apps import AppConfig


class ProjectsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.projects"
    verbose_name = "Projets"
    verbose_name_plural = "Projets"

    def ready(self):
        try:
            import apps.projects.signals  # noqa
        except ImportError:
            pass
