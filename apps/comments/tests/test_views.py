import pytest
from http import HTTPStatus
from django.urls import reverse
from django.test import Client
from apps.comments.models import Comment
from apps.tasks.models import Task
from apps.accounts.models import User
from django.contrib.messages import get_messages

HTTP_200_OK = HTTPStatus.OK
HTTP_302_REDIRECT = HTTPStatus.FOUND
HTTP_404_NOT_FOUND = HTTPStatus.NOT_FOUND
HTTP_422_UNPROCESSABLE_ENTITY = HTTPStatus.UNPROCESSABLE_ENTITY


class TestCommentCreateView:
    @pytest.mark.django_db(transaction=True)
    def test_page_success(self, client: Client, user: User, task: Task):
        client.force_login(user)
        url = reverse("comments:create", kwargs={"task_id": task.pk})
        response = client.get(url)
        assert response.status_code == HTTP_200_OK
        templates = [template.name for template in response.templates]
        assert "comments/create.html" in templates

    @pytest.mark.django_db(transaction=True)
    def test_create_submission(self, client: Client, user: User, task: Task):
        client.force_login(user)
        url = reverse("comments:create", kwargs={"task_id": task.pk})
        data = {"content": "This is a comment test."}

        response = client.post(url, data)
        url = reverse("task_detail", kwargs={"pk": task.pk})
        assert response.status_code == HTTP_302_REDIRECT
        assert response.headers["Location"] == url

        comment = Comment.objects.filter(task=task, author=user).first()
        assert comment is not None
        assert comment.content == "This is a comment test."
        assert comment.task == task
        assert comment.author == user

        messages = list(get_messages(response.wsgi_request))
        assert any(
            message.tags == "success"
            and message.message == "The comment has been successfully created."
            for message in messages
        )

    @pytest.mark.django_db(transaction=True)
    def test_create_submission_invalid_data(
        self, client: Client, user: User, task: Task
    ):
        client.force_login(user)
        url = reverse("comments:create", kwargs={"task_id": task.pk})
        response = client.post(url, {"content": ""})
        assert response.status_code == HTTP_422_UNPROCESSABLE_ENTITY

        assert response.context["form"].errors["content"] == [
            "This field is required."
        ]  # The comment content is required. vrai message apres avoire regler exception
        messages = list(get_messages(response.wsgi_request))
        assert any(
            message.tags == "error"
            and message.message
            == "The form contains errors. Please correct the marked fields."
            for message in messages
        )


class TestCommentListView:
    @pytest.mark.django_db(transaction=True)
    def test_page_success(self, client: Client, user: User, task: Task):
        client.force_login(user)
        url = reverse("comments:list", kwargs={"task_id": task.pk})
        response = client.get(url)
        assert response.status_code == HTTP_200_OK
        templates = [template.name for template in response.templates]
        assert "comments/list.html" in templates

    @pytest.mark.django_db(transaction=True)
    def test_with_comment(
        self, client: Client, user: User, task: Task, comment: Comment
    ):
        client.force_login(user)
        url = reverse("comments:list", kwargs={"task_id": task.pk})
        response = client.get(url)
        assert response.status_code == HTTP_200_OK
        assert len(response.context["comments"]) == 1
        assert "comments" in response.context
        assert "task" in response.context
        assert response.context["comments"][0] == comment
        assert response.context["task"] == task

    @pytest.mark.django_db(transaction=True)
    def test_comment_list_view_no_comments(
        self, client: Client, user: User, task_without_comments: Task
    ):
        client.force_login(user)
        url = reverse("comments:list", kwargs={"task_id": task_without_comments.pk})
        response = client.get(url)
        assert response.status_code == HTTP_200_OK
        assert len(response.context["comments"]) == 0


class TestCommentUpdateView:
    @pytest.mark.django_db(transaction=True)
    def test_page_success(
        self, client: Client, user: User, task: Task, comment: Comment
    ):
        client.force_login(user)
        url = reverse("comments:update", kwargs={"pk": comment.pk})
        response = client.get(url)
        assert response.status_code == HTTP_200_OK
        templates = [template.name for template in response.templates]
        assert "comments/update.html" in templates

    @pytest.mark.django_db(transaction=True)
    def test_update_submission(
        self, client: Client, user: User, task: Task, comment: Comment
    ):
        client.force_login(user)
        url = reverse("comments:update", kwargs={"pk": comment.pk})
        data = {"content": "This is a new comment test."}

        response = client.post(url, data)
        url_redirect = reverse("task_detail", kwargs={"pk": task.pk})
        assert response.status_code == HTTP_302_REDIRECT
        assert response.headers["Location"] == url_redirect

        comment.refresh_from_db()
        assert comment.content == "This is a new comment test."
        assert comment.task == task
        assert comment.author == user

        messages = list(get_messages(response.wsgi_request))
        assert any(
            message.tags == "success"
            and message.message == "The comment has been successfully updated."
            for message in messages
        )

    @pytest.mark.django_db(transaction=True)
    def test_update_submission_invalid_data(
        self, client: Client, user: User, task: Task, comment: Comment
    ):
        client.force_login(user)
        url = reverse("comments:update", kwargs={"pk": comment.pk})
        response = client.post(url, {"content": ""})
        assert response.status_code == HTTP_422_UNPROCESSABLE_ENTITY

        assert response.context["form"].errors["content"] == ["This field is required."]

        messages = list(get_messages(response.wsgi_request))
        assert any(
            message.tags == "error"
            and message.message
            == "The form contains errors. Please correct the marked fields."
            for message in messages
        )


class TestCommentDeleteView:
    @pytest.mark.django_db(transaction=True)
    def test_delete(self, client: Client, user: User, task: Task, comment: Comment):
        client.force_login(user)
        url = reverse("comments:delete", kwargs={"pk": comment.pk})
        response = client.post(url)

        url_redirect = reverse("task_detail", kwargs={"pk": task.pk})
        assert response.status_code == HTTP_302_REDIRECT
        assert response.headers["Location"] == url_redirect
        assert Comment.objects.filter(id=comment.pk).first() is None

        messages = list(get_messages(response.wsgi_request))
        assert any(
            message.tags == "success"
            and message.message == "The comment has been successfully deleted."
            for message in messages
        )
