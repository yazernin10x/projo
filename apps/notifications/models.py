from django.db import models
from apps.accounts.models import User


class Notification(models.Model):
    title: models.CharField = models.CharField(max_length=50, blank=False, null=False)
    content: models.CharField = models.CharField(
        max_length=200, blank=False, null=False
    )
    created_at: models.DateTimeField = models.DateTimeField(auto_now_add=True)
    is_read: models.BooleanField = models.BooleanField(default=False)
    sender: models.ForeignKey = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="send_notifications",
        verbose_name="Sender",
    )
    recipients: models.ManyToManyField = models.ManyToManyField(
        User, related_name="received_notifications", verbose_name="Recipients"
    )

    def __str__(self):
        return f"{self.title}"

    def __repr__(self):
        return f"Notification(pk={self.pk}, title='{self.title}')"
