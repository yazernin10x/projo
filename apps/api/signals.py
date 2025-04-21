from django.db.models.signals import post_save, pre_save, pre_delete
from django.dispatch import receiver
from django.utils import timezone
from .models import APIKey, APILog
from apps.core.logging import get_logger
from django.urls import reverse

logger = get_logger("api.signals")


@receiver(pre_save, sender=APIKey)
def api_key_pre_save(sender, instance, **kwargs):
    """
    Signal déclenché avant la sauvegarde d'une clé API

    Args:
        sender: Le modèle qui envoie le signal (APIKey)
        instance: L'instance de la clé API qui va être sauvegardée
        **kwargs: Arguments additionnels
    """
    try:
        if not instance.name:
            instance.name = f"API Key - {timezone.now().strftime('%Y%m%d%H%M%S')}"
        logger.info(
            f"Préparation de la sauvegarde de la clé API: {instance.name} "
            f"pour l'utilisateur: {instance.user.username}"
        )
    except Exception as e:
        logger.error(
            f"Erreur lors de la préparation de la sauvegarde de la clé API: {str(e)}"
        )
        raise


@receiver(post_save, sender=APIKey)
def api_key_post_save(sender, instance, created, **kwargs):
    """
    Signal déclenché après la sauvegarde d'une clé API

    Args:
        sender: Le modèle qui envoie le signal
        instance: L'instance de la clé API qui a été sauvegardée
        created: Boolean indiquant si c'est une création ou une mise à jour
        **kwargs: Arguments additionnels
    """
    try:
        action = "créée" if created else "mise à jour"
        logger.info(
            f"Clé API {instance.name} {action} avec succès "
            f"pour l'utilisateur: {instance.user.username}"
        )
    except Exception as e:
        logger.error(f"Erreur lors de la post-sauvegarde de la clé API: {str(e)}")
        raise


@receiver(pre_delete, sender=APIKey)
def api_key_pre_delete(sender, instance, **kwargs):
    """
    Signal déclenché avant la suppression d'une clé API

    Args:
        sender: Le modèle qui envoie le signal
        instance: L'instance de la clé API qui va être supprimée
        **kwargs: Arguments additionnels
    """
    try:
        logger.info(
            f"Suppression de la clé API: {instance.name} "
            f"pour l'utilisateur: {instance.user.username}"
        )
    except Exception as e:
        logger.error(f"Erreur lors de la suppression de la clé API: {str(e)}")
        raise


@receiver(post_save, sender=APILog)
def api_log_post_save(sender, instance, created, **kwargs):
    """
    Signal déclenché après la sauvegarde d'un log API

    Args:
        sender: Le modèle qui envoie le signal
        instance: L'instance du log API qui a été sauvegardée
        created: Boolean indiquant si c'est une création ou une mise à jour
        **kwargs: Arguments additionnels
    """
    try:
        if created:
            logger.info(
                f"Nouveau log API créé - Endpoint: {instance.endpoint}, "
                f"Méthode: {instance.method}, Status: {instance.status}"
            )

            if instance.api_key:
                api_key = instance.api_key
                api_key.last_used_at = instance.timestamp
                api_key.save(update_fields=["last_used_at"])
                logger.debug(
                    f"Mise à jour du last_used_at pour la clé API: {api_key.name}"
                )
    except Exception as e:
        logger.error(f"Erreur lors de la création du log API: {str(e)}")
        raise
