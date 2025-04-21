from django.db.models.signals import post_save, post_delete, m2m_changed
from django.dispatch import receiver

from apps.tasks.models import Task
from apps.notifications.utils import create_notification
from apps.core.middleware import get_current_request
from apps.accounts.models import User
from apps.core.logging import get_logger

logger = get_logger("tasks.signals")


@receiver(post_save, sender=Task)
def task_post_save(sender, instance, created, **kwargs):
    request = get_current_request()
    try:
        if (instance.author != instance.project.author) and request:
            # Notification pour la création de la tache
            if created:
                logger.info(
                    f"{request.user.username} a créé une nouvelle tâche dans le projet {instance.project.title}"
                )
                title = "Nouvelle tâche créée"
                content = (
                    f"{instance.author.username} a créé une nouvelle tâche '{instance.title}'"
                    f" dans votre projet '{instance.project.title}'"
                )
                create_notification(
                    request.user, [instance.project.author], title, content
                )

            # Notification pour la mise à jour de la tache
            else:
                logger.info(
                    f"{request.user.username} a modifié la tâche '{instance.title}'"
                )
                title = "Tâche modifiée"
                content = (
                    f"{instance.author.username} a modifié la tâche '{instance.title}'"
                )
                create_notification(request.user, [instance.author], title, content)
    except Exception as e:
        logger.error(f"Erreur lors du traitement du signal post_save de Task: {str(e)}")


@receiver(post_delete, sender=Task)
def task_post_delete(sender, instance, **kwargs):
    request = get_current_request()
    if (instance.author != instance.project.author) and request:
        logger.info(f"{request.user.username} a supprimé la tâche '{instance.title}'")
        title = "Tâche supprimée"
        content = (
            f"{instance.author.username} a supprimé la tâche '{instance.title}'"
            f" dans votre projet '{instance.project.title}'"
        )
        create_notification(request.user, [instance.project.author], title, content)


@receiver(m2m_changed, sender=Task.assigned_to.through)
def task_assignments_changed(sender, instance, action, pk_set, **kwargs):
    """
    Signal envoyé lorsque les assignations de la tâche changent.
    Crée des notifications pour les utilisateurs nouvellement assignés ou désassignés.
    """
    request = get_current_request()
    try:
        if (instance.author == instance.project.author) and request:
            if action == "post_add" and pk_set:
                # Notifier les nouveaux utilisateurs assignés
                users = User.objects.filter(pk__in=pk_set, is_active=True)
                logger.info(
                    f"{request.user.username} a assigné la tâche '{instance.title}'"
                    f" dans le projet '{instance.project.title}' à {list(users)}"
                )
                title = "Nouvelle assignation de tâche"
                content = (
                    f"{instance.author.username} vous a assigné la tâche '{instance.title}'"
                    f" dans le projet '{instance.project.title}'"
                )
                create_notification(request.user, list(users), title, content)

            if action == "post_remove" and pk_set:
                # Notifier les utilisateurs désassignés
                users = User.objects.filter(pk__in=pk_set, is_active=True)
                logger.info(
                    f"{request.user.username} a retiré la tâche '{instance.title}'"
                    f" dans le projet '{instance.project.title}' à {list(users)}"
                )
                title = "Retrait d'assignation de tâche"
                content = (
                    f"{instance.author.username} vous a retiré de la tâche '{instance.title}'"
                    f" dans le projet '{instance.project.title}'"
                )
                create_notification(request.user, list(users), title, content)
    except Exception as e:
        logger.error(
            f"Erreur lors du traitement du signal m2m_changed de Task: {str(e)}"
        )
