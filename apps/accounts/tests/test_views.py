from http import HTTPStatus

import pytest
from django.test import Client
from django.urls import reverse
from django.contrib.messages import get_messages
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.contrib.auth.tokens import default_token_generator

from core.settings import LOGIN_REDIRECT_URL, LOGOUT_REDIRECT_URL


from ..models import User
from .conftest import PASSWORD, USERNAME

HTTP_302_REDIRECT = HTTPStatus.FOUND
HTTP_200_OK = HTTPStatus.OK
HTTP_422_UNPROCESSABLE_ENTITY = HTTPStatus.UNPROCESSABLE_ENTITY


class TestLoginView:
    @pytest.mark.django_db(transaction=True)
    def test_page_access(self, client: Client, user: User):
        response = client.get(reverse("accounts:login"))
        assert response.status_code == HTTP_200_OK
        templates = [template.name for template in response.templates]
        assert "accounts/login.html" in templates

    @pytest.mark.django_db(transaction=True)
    def test_submission(self, client: Client, user: User):
        credentials = {"username": USERNAME, "password": PASSWORD}
        response = client.post(reverse("accounts:login"), credentials)
        assert response.status_code == HTTP_302_REDIRECT
        assert response.headers["Location"] == LOGIN_REDIRECT_URL


class TestLogoutView:
    @pytest.mark.django_db(transaction=True)
    def test_logout(self, client: Client, user: User):
        client.login(username=USERNAME, password=PASSWORD)
        response = client.post(reverse("accounts:logout"))
        assert response.status_code == HTTP_302_REDIRECT
        assert response.headers["Location"] == LOGOUT_REDIRECT_URL


class TestRegisterView:
    @pytest.mark.django_db(transaction=True)
    def test_page_access(self, client: Client):
        response = client.get(reverse("accounts:register"))
        assert response.status_code == HTTP_200_OK
        templates = [template.name for template in response.templates]
        assert "accounts/register.html" in templates

    @pytest.mark.django_db(transaction=True)
    def test_valid_submission(self, client: Client, form_data: dict):
        data = {**form_data, "password1": PASSWORD, "password2": PASSWORD}
        response = client.post(reverse("accounts:register"), data)
        assert response.status_code == HTTP_302_REDIRECT
        assert response.headers["Location"] == LOGIN_REDIRECT_URL
        user = User.objects.get(username=form_data["username"])
        assert user is not None
        assert user.first_name == form_data["first_name"]
        assert user.last_name == form_data["last_name"]
        assert user.email == form_data["email"]

        messages = list(get_messages(response.wsgi_request))
        assert any(
            message.message == "Your account has been created successfully!"
            and message.level_tag == "success"
            for message in messages
        )

    @pytest.mark.django_db(transaction=True)
    def test_invalid_submission(self, client: Client):
        data_invalid = {"first_name": "test"}
        response = client.post(reverse("accounts:register"), data_invalid)
        assert response.status_code == HTTP_422_UNPROCESSABLE_ENTITY
        templates = [template.name for template in response.templates]
        assert "accounts/register.html" in templates

        messages = list(get_messages(response.wsgi_request))
        assert any(
            message.message == "Your accounts contains errors"
            and message.level_tag == "error"
            for message in messages
        )


class TestProfileView:
    @pytest.mark.django_db(transaction=True)
    def test_page_access(self, client: Client, user: User):
        client.login(username=USERNAME, password=PASSWORD)
        response = client.get(reverse("accounts:profile"))
        assert response.status_code == HTTP_200_OK
        templates = [template.name for template in response.templates]
        assert "accounts/profile.html" in templates

    @pytest.mark.django_db(transaction=True)
    def test_valid_update_submission(self, client: Client, user: User):
        client.login(username=USERNAME, password=PASSWORD)
        response = client.post(
            reverse("accounts:profile"),
            {
                "first_name": "jane",
                "last_name": "doe",
                "username": "jane.doe",
                "email": "jane.doe@example.com",
            },
        )
        assert response.status_code == HTTP_302_REDIRECT
        assert response.headers["Location"] == reverse("accounts:profile")

        messages = list(get_messages(response.wsgi_request))
        assert any(
            message.message == "Your profile has been updated!"
            and message.level_tag == "success"
            for message in messages
        )
        user.refresh_from_db()
        assert user.first_name == "jane"
        assert user.last_name == "doe"
        assert user.username == "jane.doe"
        assert user.email == "jane.doe@example.com"

    @pytest.mark.django_db(transaction=True)
    def test_profile_invalid_data(self, client: Client, user: User):
        client.login(username=USERNAME, password=PASSWORD)

        response = client.post(
            reverse("accounts:profile"),
            {"first_name": "test"},
        )
        assert response.status_code == HTTP_422_UNPROCESSABLE_ENTITY
        templates = [template.name for template in response.templates]
        assert "accounts/profile.html" in templates

        messages = list(get_messages(response.wsgi_request))
        assert any(
            message.message == "Your profile contains errors"
            and message.level_tag == "error"
            for message in messages
        )


class TestDeleteView:
    @pytest.mark.django_db(transaction=True)
    def test_page_access(self, client: Client, user: User):
        client.login(username=USERNAME, password=PASSWORD)
        response = client.get(reverse("accounts:delete"))
        assert response.status_code == HTTP_200_OK
        templates = [template.name for template in response.templates]
        assert "accounts/user_confirm_delete.html" in templates

    @pytest.mark.django_db(transaction=True)
    def test_delete_submission(self, client: Client, user: User):
        client.login(username=USERNAME, password=PASSWORD)
        response = client.post(reverse("accounts:delete"))
        assert response.status_code == HTTP_302_REDIRECT
        assert response.headers["Location"] == reverse("index")

        messages = list(get_messages(response.wsgi_request))
        assert any(
            message.message == "Your account has been deleted successfully!"
            and message.level_tag == "success"
            for message in messages
        )
        assert not User.objects.filter(username=USERNAME).exists()


class TestPasswordChangeView:
    @pytest.mark.django_db(transaction=True)
    def test_password_change_view(self, client: Client, user: User):
        client.login(username=USERNAME, password=PASSWORD)
        response = client.get(reverse("accounts:password_change"))
        assert response.status_code == HTTP_200_OK
        templates = [template.name for template in response.templates]
        assert "accounts/password_change_form.html" in templates

    @pytest.mark.django_db(transaction=True)
    def test_password_change_done_view(self, client: Client, user: User):
        client.login(username=USERNAME, password=PASSWORD)
        response = client.get(reverse("accounts:password_change_done"))
        assert response.status_code == HTTP_200_OK
        templates = [template.name for template in response.templates]
        assert "accounts/password_change_done.html" in templates

    @pytest.mark.django_db(transaction=True)
    def test_password_reset_view(self, client: Client, user: User):
        client.login(username=USERNAME, password=PASSWORD)
        response = client.get(reverse("accounts:password_reset"))
        assert response.status_code == HTTP_200_OK
        templates = [template.name for template in response.templates]
        assert "accounts/password_reset_form.html" in templates

    @pytest.mark.django_db(transaction=True)
    def test_password_reset_done_view(self, client: Client, user: User):
        client.login(username=USERNAME, password=PASSWORD)
        response = client.get(reverse("accounts:password_reset_done"))
        assert response.status_code == HTTP_200_OK
        templates = [template.name for template in response.templates]
        assert "accounts/password_reset_done.html" in templates

    @pytest.mark.django_db(transaction=True)
    def test_password_reset_confirm_view(self, client: Client, user: User):
        client.login(username=USERNAME, password=PASSWORD)
        # Générer un UID et un token valides
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)
        url = reverse(
            "accounts:password_reset_confirm",
            kwargs={"uidb64": uid, "token": token},
        )
        response = client.get(url)
        assert response.status_code == HTTP_200_OK
        templates = [template.name for template in response.templates]
        assert "accounts/password_reset_confirm.html" in templates

    @pytest.mark.django_db(transaction=True)
    def test_password_reset_complete_view(self, client: Client, user: User):
        client.login(username=USERNAME, password=PASSWORD)
        response = client.get(reverse("accounts:password_reset_complete"))
        assert response.status_code == HTTP_200_OK
        templates = [template.name for template in response.templates]
        assert "accounts/password_reset_complete.html" in templates
