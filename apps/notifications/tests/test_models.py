from datetime import datetime

import pytest

from apps.accounts.models import User
from apps.notifications.models import Notification
from apps.notifications.tests.conftest import NOTIFICATION_MESSAGE


@pytest.mark.django_db
class TestNotification:
    def test_creation(self, user: User, notification: Notification):
        assert notification.message == NOTIFICATION_MESSAGE
        assert notification.is_read is False
        assert notification.users.first() == user
        assert isinstance(notification.created_at, datetime)

    def test__str__is_not_read(self, notification: Notification):
        expected_str = (
            f"{NOTIFICATION_MESSAGE} "
            f"(unread, "
            f"{notification.created_at.strftime('%Y-%m-%d %H:%M')})"
        )
        assert str(notification) == expected_str

    def test__str__is_read(self, notification: Notification):
        notification.is_read = True
        notification.save()
        expected_str = (
            f"{NOTIFICATION_MESSAGE} "
            f"(read, "
            f"{notification.created_at.strftime('%Y-%m-%d %H:%M')})"
        )
        assert str(notification) == expected_str

    def test__repr__(self, notification: Notification):
        expected_repr = (
            f"<Notification(id={notification.pk}, "
            f"message='{NOTIFICATION_MESSAGE}', "
            f"is_read={notification.is_read}, "
            f"created_at='{notification.created_at}', "
            f"users={notification.users})>"
        )
        assert repr(notification) == expected_repr
