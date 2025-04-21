from django.db.models.signals import m2m_changed
from django.dispatch import receiver
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from apps.notifications.models import Notification

from apps.core.logging import get_logger

logger = get_logger("notifications.signals")


@receiver(m2m_changed, sender=Notification.recipients.through)
def send_notification(sender, instance, action, pk_set, **kwargs):
    """Envoie une notification via websocket à plusieurs utilisateurs."""
    if action == "post_add":
        try:
            channel_layer = get_channel_layer()
            for recipient in instance.recipients.all():
                group_name = f"user_{recipient.pk}"
                async_to_sync(channel_layer.group_send)(
                    group_name,
                    {
                        "type": "send_notification",
                        "title": instance.title,
                        "content": instance.content,
                    },
                )
                logger.info(f"Notification websocket envoyée à {recipient.username}")
        except Exception as e:
            usernames = list(instance.recipients.values_list("username", flat=True))
            logger.error(
                f"Erreur lors de l'envoi de la notification websocket aux utilisateurs {usernames}: {e}"
            )
            raise
