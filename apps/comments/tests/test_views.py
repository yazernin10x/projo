import pytest
from django.urls import reverse
from django.test import Client
from apps.comments.models import Comment
from apps.tasks.models import Task
from apps.accounts.models import User
from apps.core.constants import HTTP_200_OK, HTTP_302_REDIRECT, COMMENT_CONTENT

from apps.core.tests.helpers import assert_message_present


@pytest.mark.django_db(transaction=True)
class TestCommentCreateView:
    def test_page_success(self, client: Client, user_1_connected: User, task: Task):
        url = reverse("comments:create", kwargs={"task_pk": task.pk})
        response = client.get(url)
        assert response.status_code == HTTP_200_OK
        assert response.context["task"] == task
        assert response.templates[0].name == "comments/comment_form_modal.html"

    def test_create_submission_valid_data(
        self, client: Client, user_1_connected: User, task: Task
    ):
        url = reverse("comments:create", kwargs={"task_pk": task.pk})
        response = client.post(url, {"content": COMMENT_CONTENT})

        url_expected = reverse("tasks:detail", kwargs={"pk": task.pk})
        assert response.status_code == HTTP_302_REDIRECT
        assert response.headers["Location"] == url_expected

        comment = Comment.objects.filter(task=task, author=user_1_connected).first()
        assert comment is not None
        assert comment.content == COMMENT_CONTENT
        assert comment.task == task
        assert comment.author == user_1_connected
        assert_message_present(response, "Le commentaire a été créé avec succès.")

    def test_create_submission_invalid_data(
        self, client: Client, user_1_connected: User, task: Task
    ):
        url = reverse("comments:create", kwargs={"task_pk": task.pk})
        response = client.post(url, {"content": ""})
        assert response.status_code == HTTP_200_OK
        assert response.templates[0].name == "comments/comment_form_modal.html"
        assert response.context["form"].errors["content"] == [
            "Ce champ est obligatoire."
        ]


@pytest.mark.django_db(transaction=True)
class TestCommentUpdateView:
    def test_page_success(
        self, client: Client, user_1_connected: User, comment: Comment
    ):
        url = reverse("comments:update", kwargs={"pk": comment.pk})
        response = client.get(url)
        assert response.status_code == HTTP_200_OK
        assert response.templates[0].name == "comments/comment_form_modal.html"

    def test_update_submission_valid_data(
        self, client: Client, user_1_connected: User, task: Task, comment: Comment
    ):
        url = reverse("comments:update", kwargs={"pk": comment.pk})
        response = client.post(url, {"content": COMMENT_CONTENT})
        url_redirect = reverse("tasks:detail", kwargs={"pk": task.pk})
        assert response.status_code == HTTP_302_REDIRECT
        assert response.headers["Location"] == url_redirect

        comment.refresh_from_db()
        assert comment.content == COMMENT_CONTENT
        assert comment.task == task
        assert comment.author == user_1_connected
        assert_message_present(response, "Le commentaire a été modifié avec succès.")

    def test_update_submission_invalid_data(
        self, client: Client, user_1_connected: User, task: Task, comment: Comment
    ):
        url = reverse("comments:update", kwargs={"pk": comment.pk})
        response = client.post(url, {"content": ""})
        assert response.status_code == HTTP_200_OK
        assert response.templates[0].name == "comments/comment_form_modal.html"
        assert response.context["form"].errors["content"] == [
            "Ce champ est obligatoire."
        ]


@pytest.mark.django_db(transaction=True)
class TestCommentDeleteView:
    def test_delete(
        self, client: Client, user_1_connected: User, task: Task, comment: Comment
    ):
        url = reverse("comments:delete", kwargs={"pk": comment.pk})
        response = client.post(url)

        url_redirect = reverse("tasks:detail", kwargs={"pk": task.pk})
        assert response.status_code == HTTP_302_REDIRECT
        assert response.headers["Location"] == url_redirect
        assert Comment.objects.filter(id=comment.pk).first() is None
        assert_message_present(response, "Le commentaire a été supprimé avec succès.")
