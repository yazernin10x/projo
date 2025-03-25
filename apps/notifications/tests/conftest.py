import pytest
from apps.accounts.models import User
from apps.notifications.models import Notification

USER_FIRST_NAME = "John"
USER_LAST_NAME = "Doe"
USERNAME = "john.doe"
USER_EMAIL = "john.doe@example.com"
USER_PASSWORD = "zootoR587"

NOTIFICATION_MESSAGE = "Test notification"
NOTIFICATION_IS_READ = False

HTTP_200_OK = 200
HTTP_302_FOUND = 302
HTTP_404_NOT_FOUND = 404
HTTP_422_UNPROCESSABLE_ENTITY = 422


@pytest.fixture(scope="function")
def user(db):
    return User.objects.create_user(
        first_name=USER_FIRST_NAME,
        last_name=USER_LAST_NAME,
        username=USERNAME,
        email=USER_EMAIL,
        password=USER_PASSWORD,
    )


@pytest.fixture(scope="function")
def notification(db, user: User):
    notify = Notification.objects.create(message=NOTIFICATION_MESSAGE)
    notify.users.add(user)
    notify.save()
    return notify


@pytest.fixture
def many_notifications(user: User):
    notif_1 = Notification.objects.create(message="Notification 1")
    notif_1.users.add(user)
    notif_1.save()

    notif_2 = Notification.objects.create(message="Notification 2")
    notif_2.users.add(user)
    notif_2.save()

    notif_3 = Notification.objects.create(message="Notification 3")
    notif_3.users.add(user)
    notif_3.save()

    return [notif_1, notif_2, notif_3]


@pytest.fixture
def valid_notification_data():
    return {
        "message": NOTIFICATION_MESSAGE,
        "is_read": NOTIFICATION_IS_READ,
        "users": None,
    }
