import pytest
from django.core.exceptions import ValidationError

from apps.accounts.tests.conftest import (
    PASSWORD,
    FIRST_NAME,
    LAST_NAME,
    USERNAME,
    EMAIL,
)

from ..models import User


class TestUserModel:
    @pytest.mark.django_db(transaction=True)
    def test_resgister(self, user: User):
        assert user.first_name == FIRST_NAME
        assert user.last_name == LAST_NAME
        assert user.username == USERNAME
        assert user.email == EMAIL
        assert user.check_password(PASSWORD)

    @pytest.mark.django_db(transaction=True)
    def test__str__(self, user: User):
        assert str(user) == f"{USERNAME} - {EMAIL}"

    @pytest.mark.django_db(transaction=True)
    def test__repr__(self, user: User):
        assert repr(user) == f"User(username='{USERNAME}', email='{EMAIL}')"

    @pytest.mark.django_db(transaction=True)
    def test_full_name(self, user: User):
        assert user.full_name == f"{FIRST_NAME} {LAST_NAME}"

    @pytest.mark.django_db(transaction=True)
    def test_duplicate_email(self, user: User, form_data: dict):
        with pytest.raises(ValidationError, match="['Email already in use.']"):
            User.objects.create_user(**form_data, password=PASSWORD).full_clean()

    @pytest.mark.django_db(transaction=True)
    def test_duplicate_username(self, user: User, form_data: dict):
        with pytest.raises(ValidationError, match="['Username already in use.']"):
            User.objects.create_user(**form_data, password=PASSWORD).full_clean()

    @pytest.mark.django_db(transaction=True)
    def test_reserved_username(self, user: User, form_data: dict):
        with pytest.raises(
            ValidationError, match="['The username 'admin' is reserved.']"
        ):
            form_data["username"] = "admin"
            User.objects.create_user(**form_data, password=PASSWORD).full_clean()

    @pytest.mark.django_db(transaction=True)
    def test_auto_timestamps(self, user: User):
        assert user.created_at is not None
        assert user.updated_at is not None
