from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from apps.notifications.utils import create_notification
from apps.core.middleware import get_current_request
from apps.comments.models import Comment

from apps.core.logging import get_logger

logger = get_logger("comments.signals")


@receiver(post_save, sender=Comment)
def notify_task_owner_on_comment(sender, instance, created, **kwargs):
    """
    Envoie une notification au propriétaire de la tâche lorsqu'un commentaire est créé ou modifié.
    """
    request = get_current_request()

    if (instance.task.author != instance.author) and request:
        if created:
            # Notification pour un nouveau commentaire
            logger.info(
                f"{request.user.username} a commenté la tâche de {instance.task.title}"
            )
            title = "Nouveau commentaire"
            content = f"{instance.author.username} a commenté votre tâche '{instance.task.title}'"
            create_notification(request.user, [instance.task.author], title, content)

        else:
            # Notification pour un commentaire modifié
            logger.info(
                f"{request.user.username} a modifié son commentaire sur la tâche {instance.task.title}"
            )
            title = "Commentaire modifié"
            content = f"{instance.author.username} a modifié son commentaire sur votre tâche '{instance.task.title}'"
            create_notification(request.user, [instance.task.author], title, content)


@receiver(post_delete, sender=Comment)
def notify_comment_deletion(sender, instance, **kwargs):
    """
    Envoie une notification au propriétaire de la tâche lorsqu'un commentaire est supprimé.
    """
    request = get_current_request()
    if (instance.task.author != instance.author) and request:
        logger.info(
            f"{request.user.username} à supprimé un commentaire sur la tâche de {instance.task.title}"
        )
        title = "Commentaire supprimé"
        content = f"{instance.author.username} a supprimé un commentaire sur votre tâche '{instance.task.title}'"
        create_notification(request.user, [instance.task.author], title, content)
