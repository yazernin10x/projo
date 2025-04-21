from datetime import datetime

import pytest

from apps.accounts.models import User
from apps.notifications.models import Notification
from apps.core.constants import (
    NOTIFICATION_TITLE,
    NOTIFICATION_CONTENT,
)


@pytest.mark.django_db
class TestNotification:
    def test_creation(self, user_2_connected: User, notification: Notification):
        assert notification.title == NOTIFICATION_TITLE
        assert notification.content == NOTIFICATION_CONTENT
        assert notification.is_read is False
        assert notification.recipients.first() == user_2_connected
        assert isinstance(notification.created_at, datetime)

    def test__str__(self, notification: Notification):
        assert str(notification) == NOTIFICATION_TITLE

    def test__repr__(self, notification: Notification):
        notification.refresh_from_db()
        assert (
            repr(notification)
            == f"Notification(pk={notification.pk}, title='{NOTIFICATION_TITLE}')"
        )
