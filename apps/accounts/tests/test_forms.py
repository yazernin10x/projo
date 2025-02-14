import pytest
from django.core.exceptions import ValidationError

from ..forms import UserRegisterForm, UserUpdateForm


class TestUserForms:
    @pytest.mark.django_db(transaction=True)
    def test_register_form(self, form_data: dict):
        form = UserRegisterForm(
            data={
                "password1": "testpassword",
                "password2": "testpassword",
                **form_data,
            }
        )
        assert form.is_valid() is True
        assert form.cleaned_data["first_name"] == form_data["first_name"]
        assert form.cleaned_data["last_name"] == form_data["last_name"]
        assert form.cleaned_data["username"] == form_data["username"]
        assert form.cleaned_data["email"] == form_data["email"]
        assert form.cleaned_data["phone_number"] == form_data["phone_number"]

    @pytest.mark.django_db(transaction=True)
    def test_register_form_passwords_non_match(self, form_data: dict):
        form = UserRegisterForm(
            data={
                **form_data,
                "password1": "password1",
                "password2": "password2",
            }
        )
        with pytest.raises(ValidationError):
            form.full_clean()

    @pytest.mark.django_db(transaction=True)
    def test_register_form_clean_phone_number_invalid(self, form_data: dict):
        form_data["phone_number"] = "12345"
        form = UserRegisterForm(data=form_data)
        with pytest.raises(ValidationError):
            form.full_clean()

    @pytest.mark.django_db(transaction=True)
    def test_user_update_form(self, form_data: dict):
        form_data["first_name"] = "testuser"
        form_data["email"] = "testuser@example.com"
        form = UserUpdateForm(data=form_data)
        assert form.is_valid() is True
        assert form.cleaned_data["first_name"] == "testuser"
        assert form.cleaned_data["email"] == "testuser@example.com"
