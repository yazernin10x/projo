from django.db.models.signals import post_save, post_delete, m2m_changed
from django.dispatch import receiver
from .models import Project
from apps.notifications.utils import create_notification
from apps.core.middleware import get_current_request
from apps.accounts.models import User
from apps.core.logging import get_logger

logger = get_logger("projects.signals")


@receiver(post_save, sender=Project)
def project_post_save(sender, instance, created, **kwargs):
    request = get_current_request()
    try:
        if request:
            # Notification pour la création du projet
            if created:
                logger.info(
                    f"{request.user.username} a créé un nouveau projet '{instance.title}'"
                )
                title = "Nouveau projet créé"
                content = f"{instance.author.username} a créé un nouveau projet '{instance.title}'"
                create_notification(request.user, [instance.author], title, content)
            # Notification pour la mise à jour du projet
            else:
                logger.info(
                    f"{request.user.username} a modifié le projet '{instance.title}'"
                )
                title = "Projet modifié"
                content = (
                    f"{instance.author.username} a modifié le projet '{instance.title}'"
                )
                create_notification(request.user, [instance.author], title, content)
    except Exception as e:
        logger.error(
            f"Erreur lors du traitement du signal post_save de Project: {str(e)}"
        )


@receiver(post_delete, sender=Project)
def project_post_delete(sender, instance, **kwargs):
    request = get_current_request()
    if request:
        logger.info(f"{request.user.username} a supprimé le projet '{instance.title}'")
        title = "Projet supprimé"
        content = f"{instance.author.username} a supprimé le projet '{instance.title}'"
        create_notification(request.user, [instance.author], title, content)


@receiver(m2m_changed, sender=Project.members.through)
def project_members_changed(sender, instance, action, pk_set, **kwargs):
    """
    Signal envoyé lorsque les membres du projet changent.
    Crée des notifications pour les nouveaux membres ou les membres retirés.
    """
    request = get_current_request()
    try:
        if request:
            if action == "post_add" and pk_set:
                # Notifier les nouveaux membres
                users = User.objects.filter(pk__in=pk_set, is_active=True)
                logger.info(
                    f"{request.user.username} a ajouté {list(users)} comme membres du projet '{instance.title}'"
                )
                title = "Nouveau membre du projet"
                content = f"{instance.author.username} vous a ajouté comme membre du projet '{instance.title}'"
                create_notification(request.user, list(users), title, content)

            if action == "post_remove" and pk_set:
                # Notifier les membres retirés
                users = User.objects.filter(pk__in=pk_set, is_active=True)
                logger.info(
                    f"{request.user.username} a retiré {list(users)} des membres du projet '{instance.title}'"
                )
                title = "Retrait du projet"
                content = f"{instance.author.username} vous a retiré des membres du projet '{instance.title}'"
                create_notification(request.user, list(users), title, content)
    except Exception as e:
        logger.error(
            f"Erreur lors du traitement du signal m2m_changed de Project: {str(e)}"
        )
