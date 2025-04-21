from datetime import timedelta
from django.utils import timezone
import pytest
from apps.accounts.models import User
from apps.notifications.models import Notification
from apps.core.constants import (
    NOTIFICATION_TITLE,
    NOTIFICATION_CONTENT,
)
from apps.core.tests.fixtures import (
    user_1,
    user_2,
    user_1_connected,
    user_2_connected,
)


@pytest.fixture(scope="function")
def notification(db, user_1: User, user_2: User):
    notif = Notification.objects.create(
        title=NOTIFICATION_TITLE,
        content=NOTIFICATION_CONTENT,
        sender=user_1,
    )
    notif.recipients.add(user_2)
    notif.save()
    return notif


@pytest.fixture(scope="function")
def notifications(user_1: User, user_2: User):
    today = timezone.now()
    yesterday = today - timedelta(days=1)
    last_week = today - timedelta(days=7)
    last_month = today - timedelta(days=30)

    notif_1 = Notification.objects.create(
        title="Notification Today",
        content=NOTIFICATION_CONTENT,
        is_read=False,
        sender=user_1,
    )
    notif_1.created_at = today
    notif_1.recipients.add(user_2)
    notif_1.save()

    notif_2 = Notification.objects.create(
        title="Notification Yesterday",
        content=NOTIFICATION_CONTENT,
        is_read=False,
        sender=user_1,
    )
    notif_2.created_at = yesterday
    notif_2.recipients.add(user_2)
    notif_2.save()

    notif_3 = Notification.objects.create(
        title="Notification Last Week",
        content=NOTIFICATION_CONTENT,
        is_read=True,
        sender=user_1,
    )
    notif_3.created_at = last_week
    notif_3.recipients.add(user_2)
    notif_3.save()

    notif_4 = Notification.objects.create(
        title="Notification Last Month",
        content=NOTIFICATION_CONTENT,
        is_read=True,
        sender=user_1,
    )
    notif_4.created_at = last_month
    notif_4.recipients.add(user_2)
    notif_4.save()
    return [notif_1, notif_2, notif_3, notif_4]


@pytest.fixture(scope="function")
def valid_data():
    return {
        "title": NOTIFICATION_TITLE,
        "content": NOTIFICATION_CONTENT,
        "recipients": None,
    }
