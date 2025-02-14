import pytest
from django.core.exceptions import ValidationError

from ..models import User


class TestUserModel:
    @pytest.mark.django_db(transaction=True)
    def test_resgister(self, user: User):
        assert user.first_name == "John"
        assert user.last_name == "Doe"
        assert user.username == "john.doe"
        assert user.email == "john.doe@example.com"
        assert user.check_password("password") is True

    @pytest.mark.django_db(transaction=True)
    def test__str__(self, user: User):
        assert str(user) == "john.doe - john.doe@example.com"

    @pytest.mark.django_db(transaction=True)
    def test__repr__(self, user: User):
        assert repr(user) == "User(username='john.doe', email='john.doe@example.com')"

    @pytest.mark.django_db(transaction=True)
    def test_full_name(self, user: User):
        assert user.full_name == "John Doe"

    @pytest.mark.django_db(transaction=True)
    def test_duplicate_email(self, user: User):
        with pytest.raises(ValidationError, match="['Email already in use.']"):
            User.objects.create_user(
                first_name="Jane",
                last_name="Doe",
                username="jane.doe",
                email="john.doe@example.com",
                password="password",
            ).full_clean()

    @pytest.mark.django_db(transaction=True)
    def test_duplicate_username(self, user: User):
        with pytest.raises(ValidationError, match="['Username already in use.']"):
            User.objects.create_user(
                first_name="Jane",
                last_name="Doe",
                username="john.doe",
                email="jane.doe@example.com",
                password="password",
            ).full_clean()
