import pytest
from django.core.exceptions import ValidationError

from apps.notifications.forms import NotificationForm
from apps.accounts.models import User

from .conftest import NOTIFICATION_MESSAGE


@pytest.mark.django_db
class TestNotificationForm:
    def test_form_valid_data(self, user: User):
        other_user = User.objects.create_user(
            first_name="other_user",
            last_name="other_user",
            username="other_user",
            email="other_user@example.com",
            password="test123",
        )

        form_data = {
            "message": NOTIFICATION_MESSAGE,
            "users": [user.pk, other_user.pk],
        }
        form = NotificationForm(data=form_data)
        assert form.is_valid()
        assert list(form.cleaned_data["users"]) == [user, other_user]
        assert form.cleaned_data["message"] == NOTIFICATION_MESSAGE

    def test_form_invalid_data(self, user: User):
        form_data = {"message": "", "users": [user.pk]}
        form = NotificationForm(data=form_data)
        assert not form.is_valid(), "The form should not be valid."
        assert "message" in form.errors, "The 'message' field is required."

    def test_form_users_queryset(self, user: User):
        inactive_user = User.objects.create_user(
            first_name="inactive_user",
            last_name="inactive_user",
            username="inactive_user",
            email="inactive@example.com",
            password="test123",
            is_active=False,
        )

        form = NotificationForm()
        assert (
            inactive_user not in form.fields["users"].queryset
        ), "Only one active user must be selected."

    def test_form_clean_users(self):
        form_data = {"message": NOTIFICATION_MESSAGE, "users": []}
        form = NotificationForm(data=form_data)
        with pytest.raises(ValidationError):
            form.full_clean()
