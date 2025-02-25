import pytest
from django.urls import reverse
from apps.accounts.models import User
from apps.notifications.models import Notification
from django.contrib.messages import get_messages

from apps.notifications.tests.conftest import (
    NOTIFICATION_IS_READ,
    NOTIFICATION_MESSAGE,
    USERNAME,
    USER_PASSWORD,
    HTTP_200_OK,
    HTTP_302_FOUND,
    HTTP_404_NOT_FOUND,
    HTTP_422_UNPROCESSABLE_ENTITY,
)


@pytest.mark.django_db
class TestNotificationListView:
    def test_user_is_authenticated(self, client):
        response = client.get(reverse("notifications:list"))
        assert response.status_code == HTTP_302_FOUND
        assert reverse("accounts:login") in response.headers["location"]

    def test_notification_list_view(
        self, client, many_notifications: list[Notification]
    ):
        client.login(username=USERNAME, password=USER_PASSWORD)

        response = client.get(reverse("notifications:list"))
        assert response.status_code == HTTP_200_OK
        assert "notifications" in response.context

        notifications = response.context["notifications"]
        assert len(notifications) == 3
        assert all(
            notification.message
            in ["Notification 1", "Notification 2", "Notification 3"]
            for notification in notifications
        )

        template = response.templates[0].name
        assert template == "notifications/list.html"


@pytest.mark.django_db
class TestMarkAsReadView:
    def test_mark_as_read_success(self, client, notification):
        client.login(username=USERNAME, password=USER_PASSWORD)

        url = reverse("notifications:mark_as_read", kwargs={"pk": notification.pk})
        response = client.post(url)

        notification.refresh_from_db()
        assert notification.is_read is True

        assert response.status_code == HTTP_302_FOUND
        assert response.headers["Location"] == reverse("notifications:list")

        messages = list(get_messages(response.wsgi_request))
        assert len(messages) == 1
        assert messages[0].message == "Notification marked as read"

    def test_mark_as_read_invalid_user(self, client, notification):
        other_user = User.objects.create_user(
            first_name="Other",
            last_name="User",
            username="otheruser",
            password="otherpassword",
        )
        client.force_login(other_user)
        url = reverse("notifications:mark_as_read", kwargs={"pk": notification.pk})
        response = client.post(url)

        assert response.status_code == HTTP_404_NOT_FOUND


@pytest.mark.django_db
class TestMarkAllAsReadView:
    def test_mark_all_as_read_success(
        self, client, user, many_notifications: list[Notification]
    ):
        client.force_login(user)
        response = client.post(reverse("notifications:mark_all_as_read"))

        for notification in many_notifications:
            notification.refresh_from_db()
            assert notification.is_read is True

        assert response.status_code == HTTP_302_FOUND
        assert reverse("notifications:list") in response.headers["location"]

        messages = list(get_messages(response.wsgi_request))
        assert len(messages) == 1
        assert messages[0].message == "All notifications marked as read"

    def test_mark_all_as_read_no_notifications(
        self, client, user, many_notifications: list[Notification]
    ):
        user.notifications.all().delete()
        client.force_login(user)

        response = client.post(reverse("notifications:mark_all_as_read"))

        assert response.status_code == HTTP_302_FOUND
        assert reverse("notifications:list") in response.headers["location"]

        messages = list(get_messages(response.wsgi_request))
        assert len(messages) == 1
        assert messages[0].message == "No notifications to mark as read"


@pytest.mark.django_db
class TestCreateNotificationView:

    def test_page_success(self, client):
        client.login(username=USERNAME, password=USER_PASSWORD)
        response = client.get(reverse("notifications:create"))
        assert response.status_code == HTTP_302_FOUND
        assert reverse("notifications:list") in response.headers["location"]

    def test_create_notification_success(self, client, user, valid_notification_data):
        client.login(username=USERNAME, password=USER_PASSWORD)
        valid_notification_data["users"] = [user.id]

        url = reverse("notifications:create")
        response = client.post(url, data=valid_notification_data)

        assert Notification.objects.count() == 1
        notification = Notification.objects.first()
        assert notification.message == NOTIFICATION_MESSAGE
        assert notification.is_read == NOTIFICATION_IS_READ
        assert notification.users.first() == user

        assert response.status_code == HTTP_302_FOUND
        assert reverse("notifications:list") in response.headers["location"]

        messages = list(get_messages(response.wsgi_request))
        assert len(messages) == 1
        assert messages[0].message == "Notification created successfully"

    def test_create_notification_invalid_form(self, client, user):
        client.login(username=USERNAME, password=USER_PASSWORD)
        invalid_data = {"is_read": False, "user": user.id}

        url = reverse("notifications:create")
        response = client.post(url, data=invalid_data)

        assert Notification.objects.count() == 0

        assert response.status_code == HTTP_422_UNPROCESSABLE_ENTITY
        template = response.templates[0].name
        assert template == "notifications/create.html"

        messages = list(get_messages(response.wsgi_request))
        assert len(messages) == 1
        assert messages[0].message == "Invalid form"


@pytest.mark.django_db
class TestNotificationDeleteView:
    def test_delete_notification_success(self, client, notification):
        client.login(username=USERNAME, password=USER_PASSWORD)

        url = reverse("notifications:delete", kwargs={"pk": notification.pk})
        response = client.post(url)

        assert response.status_code == HTTP_302_FOUND
        assert reverse("notifications:list") in response.headers["location"]

        assert Notification.objects.count() == 0

        messages = list(get_messages(response.wsgi_request))
        assert len(messages) == 1
        assert messages[0].message == "Notification deleted successfully"

    def test_delete_notification_invalid_user(self, client, notification):
        other_user = User.objects.create_user(
            first_name="Test",
            last_name="User",
            username="testuser",
            password="testpassword",
        )
        client.force_login(other_user)

        url = reverse("notifications:delete", kwargs={"pk": notification.pk})
        response = client.post(url)

        assert response.status_code == HTTP_404_NOT_FOUND
