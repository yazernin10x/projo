from apps.notifications.models import Notification

from apps.core.logging import get_logger

logger = get_logger("notifications.utils")


def create_notification(sender, recipients, title, content):
    try:
        notification = Notification.objects.create(
            sender=sender, title=title, content=content
        )

        # notification.recipients.through.objects.create(
        #     notification=notification,
        #     user=recipient,
        # )
        # notification.recipients.set(recipients)
        # notification.save()
    except Exception as e:
        logger.error(
            f"Erreur lors de la création de la notification pour {recipients}: {e}"
        )
        raise
    else:
        logger.info(f"Notification créée pour {recipients}")
        return notification
