import pytest
from django.urls import reverse
from django.test import Client
from apps.accounts.models import User
from apps.core.tests.helpers import assert_message_present
from apps.notifications.models import Notification
from apps.core.constants import (
    HTTP_200_OK,
    HTTP_302_REDIRECT,
)


@pytest.mark.django_db(transaction=True)
class TestNotificationListView:
    def test_page_access(
        self, client: Client, user_2_connected: User, notification: Notification
    ):
        # User 2 est le destinataire connecté dont les notifications sont affichées
        response = client.get(reverse("notifications:list"))
        assert response.status_code == HTTP_200_OK
        assert response.templates[0].name == "notifications/list.html"
        assert "notifications" in response.context
        assert response.context["notifications"].first() == notification
        assert "unread_notifications" in response.context
        assert response.context["unread_notifications"].first() == notification
        assert "read_notifications" in response.context
        assert response.context["read_notifications"].count() == 0
        assert "senders" in response.context
        assert response.context["senders"].first() == notification.sender.username

    def test_filters(
        self, client, user_2_connected: User, notifications: list[Notification]
    ):
        # Test filtre non lu
        response = client.get(reverse("notifications:list"), {"status": "unread"})
        assert len(response.context["notifications"]) == 2
        assert not response.context["notifications"][0].is_read
        assert not response.context["notifications"][1].is_read

        # Test filtre lu
        response = client.get(reverse("notifications:list"), {"status": "read"})
        assert len(response.context["notifications"]) == 2
        assert response.context["notifications"][0].is_read
        assert response.context["notifications"][1].is_read

        # Test filtre par expéditeur
        response = client.get(
            reverse("notifications:list"), {"sender": user_2_connected.username}
        )
        assert len(response.context["notifications"]) == 0

    def test_date_filters(
        self, client, user_2_connected: User, notifications: list[Notification]
    ):
        # Test filtre aujourd'hui
        response = client.get(reverse("notifications:list"), {"date": "today"})
        assert len(response.context["notifications"]) == 1
        assert response.context["notifications"][0].title == "Notification Today"

        # Test filtre cette semaine
        response = client.get(reverse("notifications:list"), {"date": "this_week"})
        notifications_this_week = response.context["notifications"]
        assert len(notifications_this_week) == 2
        assert "Notification Today" in [n.title for n in notifications_this_week]
        assert "Notification Yesterday" in [n.title for n in notifications_this_week]

        # Test filtre ce mois
        response = client.get(reverse("notifications:list"), {"date": "this_month"})
        notifications_this_month = response.context["notifications"]
        assert len(notifications_this_month) >= 2
        assert "Notification Last Month" not in [
            n.title for n in notifications_this_month
        ]


@pytest.mark.django_db(transaction=True)
class TestMarkAsReadView:
    def test_mark_as_read_success(
        self, client, user_2_connected: User, notification: Notification
    ):
        url = reverse("notifications:mark_as_read", kwargs={"pk": notification.pk})
        response = client.post(url)
        notification.refresh_from_db()
        assert notification.is_read is True
        assert response.status_code == HTTP_302_REDIRECT
        assert response.headers["Location"] == reverse("notifications:list")
        assert_message_present(response, "Notification marquée comme lue")


@pytest.mark.django_db(transaction=True)
class TestMarkAllAsReadView:
    def test_mark_all_as_read_success(
        self, client, user_2_connected: User, notifications: list[Notification]
    ):
        response = client.post(reverse("notifications:mark_all_as_read"))
        for notification in notifications:
            notification.refresh_from_db()
            assert notification.is_read is True

        assert response.status_code == HTTP_302_REDIRECT
        assert response.headers["Location"] == reverse("notifications:list")
        assert_message_present(
            response, "Toutes les notifications ont été marquées comme lues"
        )

    def test_mark_all_as_read_no_notifications(self, client, user_2_connected: User):
        response = client.post(reverse("notifications:mark_all_as_read"))
        assert response.status_code == HTTP_302_REDIRECT
        assert response.headers["Location"] == reverse("notifications:list")
        assert_message_present(
            response, "Aucune notification à marquer comme lue", "info"
        )


@pytest.mark.django_db(transaction=True)
class TestMarkAsUnreadView:
    def test_mark_as_unread_success(
        self, client, user_2_connected: User, notification: Notification
    ):
        url = reverse("notifications:mark_as_unread", kwargs={"pk": notification.pk})
        response = client.post(url)
        notification.refresh_from_db()
        assert notification.is_read is False
        assert response.status_code == HTTP_302_REDIRECT
        assert response.headers["Location"] == reverse("notifications:list")
        assert_message_present(response, "Notification marquée comme non lue")


@pytest.mark.django_db(transaction=True)
class TestMarkAllAsUnreadView:
    def test_mark_all_as_unread_success(
        self, client, user_2_connected: User, notifications: list[Notification]
    ):
        response = client.post(reverse("notifications:mark_all_as_unread"))
        for notification in notifications:
            notification.refresh_from_db()
            assert notification.is_read is False

        assert response.status_code == HTTP_302_REDIRECT
        assert response.headers["Location"] == reverse("notifications:list")
        assert_message_present(
            response, "Toutes les notifications ont été marquées comme non lues"
        )

    def test_mark_all_as_unread_no_notifications(self, client, user_2_connected: User):
        response = client.post(reverse("notifications:mark_all_as_unread"))
        assert response.status_code == HTTP_302_REDIRECT
        assert response.headers["Location"] == reverse("notifications:list")
        assert_message_present(
            response, "Aucune notification à marquer comme non lue", "info"
        )


@pytest.mark.django_db(transaction=True)
class TestNotificationDeleteView:
    def test_delete_notification_success(self, client, user_2_connected, notification):
        url = reverse("notifications:delete", kwargs={"pk": notification.pk})
        response = client.post(url)
        assert response.status_code == HTTP_302_REDIRECT
        assert response.headers["Location"] == reverse("notifications:list")
        assert Notification.objects.count() == 0
        assert_message_present(response, "Notification supprimée avec succès")


@pytest.mark.django_db(transaction=True)
class TestDeleteAllNotificationsView:
    def test_delete_all_notifications_success(
        self, client, user_2_connected, notifications
    ):
        url = reverse("notifications:delete_all")
        response = client.post(url)
        assert response.status_code == HTTP_302_REDIRECT
        assert response.headers["Location"] == reverse("notifications:list")
        assert Notification.objects.count() == 0
        assert_message_present(response, "Toutes les notifications ont été supprimées")


@pytest.mark.django_db(transaction=True)
def test_unauthorized_access(client, notification):
    urls = [
        reverse("notifications:list"),
        reverse("notifications:mark_as_read", args=[notification.pk]),
        reverse("notifications:mark_all_as_read"),
        reverse("notifications:mark_as_unread", args=[notification.pk]),
        reverse("notifications:mark_all_as_unread"),
        reverse("notifications:delete", args=[notification.pk]),
        reverse("notifications:delete_all"),
    ]

    for url in urls:
        response = client.post(url)
        assert response.status_code == HTTP_302_REDIRECT
        assert response.headers["Location"] == f"{reverse('accounts:login')}?next={url}"
