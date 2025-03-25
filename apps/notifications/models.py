from django.db.models import (
    Model,
    DateTimeField,
    BooleanField,
    ManyToManyField,
    ForeignKey,
    CASCADE,
    CharField,
)
from apps.accounts.models import User


class Notification(Model):
    sender: ForeignKey = ForeignKey(
        User,
        on_delete=CASCADE,
        related_name="sent_notifications",
        verbose_name="Sender",
    )

    recipients: ManyToManyField = ManyToManyField(
        User, related_name="received_notifications", verbose_name="Recipients"
    )

    content: CharField = CharField(max_length=200)
    created_at: DateTimeField = DateTimeField(auto_now_add=True)
    is_read: BooleanField = BooleanField(default=False)

    def __str__(self):
        read_status = "read" if self.is_read else "unread"
        return (
            f"{self.content} "
            f"({read_status}, "
            f"{self.created_at.strftime('%Y-%m-%d %H:%M')})"
        )

    def __repr__(self):
        return (
            f"<Notification("
            f"id={self.id}, "
            f"content='{self.content}', "
            f"is_read={self.is_read}, "
            f"created_at='{self.created_at}', "
            f"recipients={self.recipients.all()}, "
            f"sender={self.sender}"
            f")>"
        )
