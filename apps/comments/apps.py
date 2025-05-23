from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class CommentsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.comments"
    verbose_name = _("comments")

    def ready(self):
        try:
            import apps.comments.signals  # noqa
        except ImportError:
            pass
