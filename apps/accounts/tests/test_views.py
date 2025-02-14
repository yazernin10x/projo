from http import HTTPStatus

import pytest
from django.test import Client
from django.urls import reverse

from ..models import User
from .conftest import PASSWORD, USERNAME

HTTP_302_FOUND = HTTPStatus.FOUND


class TestUserView:
    @pytest.mark.django_db(transaction=True)
    def test_login(self, client: Client, user: User):
        response = client.get(reverse("accounts:login"))
        templates = [template.name for template in response.templates]
        assert "accounts/login.html" in templates

        response = client.post(
            reverse("accounts:login"),
            {"username": USERNAME, "password": PASSWORD},
        )
        assert response.status_code == HTTP_302_FOUND
        assert response.headers["Location"] == "/"

    @pytest.mark.django_db(transaction=True)
    def test_logout(self, client: Client, user: User):
        response = client.post(
            reverse("accounts:login"),
            {"username": USERNAME, "password": PASSWORD},
        )
        response = client.post(reverse("accounts:logout"))
        assert response.status_code == HTTP_302_FOUND
        assert response.headers["Location"] == "/"

    # def test_register_view(self):
    #     response = self.client.post(
    #         reverse("users:register"),
    #         {
    #             "username": "testuser",
    #             "email": "testuser@example.com",
    #             "password": "testpassword",
    #         },
    #     )
    #     self.assertEqual(response.status_code, 200)
    #     self.assertTemplateUsed(response, "users/register.html")

    # def test_profile_view(self):
    #     response = self.client.get(reverse("users:profile"))
    #     self.assertEqual(response.status_code, 200)
    #     self.assertTemplateUsed(response, "users/profile.html")

    # def test_password_change_view(self):
    #     response = self.client.post(
    #         reverse("users:password_change"),
    #         {
    #             "old_password": "testpassword",
    #             "new_password1": "newpassword",
    #             "new_password2": "newpassword",
    #         },
    #     )
    #     self.assertEqual(response.status_code, 200)
    #     self.assertTemplateUsed(response, "users/password_change.html")

    # def test_password_reset_view(self):
    #     response = self.client.post(
    #         reverse("users:password_reset"), {"email": "testuser@example.com"}
    #     )
    #     self.assertEqual(response.status_code, 200)
    #     self.assertTemplateUsed(response, "users/password_reset.html")

    # def test_password_reset_confirm_view(self):
    #     response = self.client.post(
    #         reverse("users:password_reset_confirm", args=["token"]),
    #         {"new_password1": "newpassword", "new_password2": "newpassword"},
    #     )
    #     self.assertEqual(response.status_code, 200)
    #     self.assertTemplateUsed(response, "users/password_reset_confirm.html")

    # def test_delete_view(self):
    #     response = self.client.post(reverse("users:delete"))
    #     self.assertEqual(response.status_code, 200)
    #     self.assertTemplateUsed(response, "users/delete.html")

    # def test_password_change_done_view(self):
    #     response = self.client.get(reverse("users:password_change_done"))
    #     self.assertEqual(response.status_code, 200)
    #     self.assertTemplateUsed(response, "users/password_change_done.html")

    # def test_password_reset_complete_view(self):
    #     response = self.client.get(reverse("users:password_reset_complete"))
    #     self.assertEqual(response.status_code, 200)
    #     self.assertTemplateUsed(response, "users/password_reset_complete.html")
