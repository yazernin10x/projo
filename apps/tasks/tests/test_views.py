import pytest
from django.urls import reverse
from django.test import Client
from apps.comments.models import Comment
from apps.tasks.models import Task
from apps.accounts.models import User
from apps.projects.models import Project
from .conftest import (
    HTTP_200_OK,
    HTTP_302_REDIRECT,
    HTTP_422_UNPROCESSABLE_ENTITY,
    TASK_STATUS,
    TASK_DESCRIPTION,
    TASK_DEADLINE,
    TASK_TITLE,
)


@pytest.mark.django_db
class TestTaskListView:
    def test_page_is_accessible(self, user: User, client: Client):
        client.force_login(user)
        response = client.get(reverse("tasks:list"))
        assert response.status_code == HTTP_200_OK
        assert response.templates[0].name == "tasks/list.html"

    def test_list_view(self, client: Client, user: User, project: Project, task: Task):
        user1 = User.objects.create_user(
            first_name="Test",
            last_name="User",
            email="testuser@example.com",
            username="testuser",
            password="password",
        )

        task1 = Task.objects.create(
            title="Test Task",
            status=TASK_STATUS,
            description=TASK_DESCRIPTION,
            deadline=TASK_DEADLINE,
            project=project,
            author=user1,
        )
        task1.assigned_to.add(user)

        client.force_login(user)
        response = client.get(reverse("tasks:list"))
        assert response.status_code == HTTP_200_OK
        assert response.context["tasks"].count() == 1
        assert response.context["tasks"][0] == task
        assert response.context["assigned_tasks"].count() == 1
        assert response.context["assigned_tasks"][0] == task1
        assert response.templates[0].name == "tasks/list.html"


@pytest.mark.django_db
class TestTaskDetailView:
    def test_page_is_accessible(self, client: Client, user: User, task: Task):
        client.force_login(user)
        response = client.get(reverse("tasks:detail", kwargs={"pk": task.pk}))
        assert response.status_code == HTTP_200_OK
        assert response.templates[0].name == "tasks/detail.html"

    @pytest.mark.django_db
    def test_task_detail_view_not_authenticated(self, client: Client, task: Task):
        response = client.get(reverse("tasks:detail", kwargs={"pk": task.pk}))

        assert response.status_code == HTTP_302_REDIRECT
        assert response.url.startswith("/accounts/login/")

    def test_detail_view_authenticated(
        self, client: Client, user: User, task: Task, comment: Comment
    ):
        client.force_login(user)
        response = client.get(reverse("tasks:detail", kwargs={"pk": task.pk}))

        assert response.status_code == HTTP_200_OK
        assert response.templates[0].name == "tasks/detail.html"

        assert response.context["task"] == task

        assert response.context["comments"].count() == 1
        assert response.context["comments"][0] == comment


@pytest.mark.django_db
class TestTaskCreateView:
    def test_page_is_accessible(self, client: Client, user: User):
        client.force_login(user)
        response = client.get(reverse("tasks:create"))
        assert response.status_code == HTTP_200_OK
        assert response.templates[0].name == "tasks/task_form.html"

    def test_task_create_view_authenticated(
        self, client: Client, user: User, project: Project, form_data: dict
    ):
        client.force_login(user)
        response = client.post(reverse("tasks:create"), form_data, follow=True)

        assert response.status_code == HTTP_200_OK
        assert Task.objects.count() == 1
        assert Task.objects.first().title == TASK_TITLE
        assert Task.objects.first().author == user
        assert Task.objects.first().project == project

        messages = list(response.context["messages"])
        assert len(messages) == 1
        assert str(messages[0]) == "Task created successfully"

    @pytest.mark.django_db
    def test_task_create_view_invalid_form(
        self, client: Client, user: User, project: Project, form_data: dict
    ):
        client.force_login(user)
        form_data["title"] = ""
        response = client.post(reverse("tasks:create"), form_data, follow=True)

        assert response.status_code == HTTP_200_OK
        assert Task.objects.count() == 0
        assert response.templates[0].name == "tasks/task_form.html"
        assert response.context["form"].errors
        assert response.context["form"].errors["title"] == ["This field is required."]

        messages = list(response.context["messages"])
        assert len(messages) == 1
        assert str(messages[0]) == "Invalid form"

    @pytest.mark.django_db
    def test_task_create_view_not_authenticated(self, client: Client):
        response = client.get(reverse("tasks:create"))
        assert response.status_code == HTTP_302_REDIRECT
        assert response.url.startswith("/accounts/login/")


@pytest.mark.django_db
class TestTaskUpdateView:
    def test_page_is_accessible(self, client: Client, user: User, task: Task):
        client.force_login(user)
        response = client.get(reverse("tasks:update", kwargs={"pk": task.pk}))
        assert response.status_code == HTTP_200_OK
        assert response.templates[0].name == "tasks/task_form.html"

    def test_task_update_view_authenticated(
        self, client: Client, user: User, project: Project, task: Task, form_data: dict
    ):
        client.force_login(user)

        del form_data["project"], form_data["author"]
        form_data["title"] = "New title"
        response = client.post(
            reverse("tasks:update", kwargs={"pk": task.pk}), form_data, follow=True
        )

        assert response.status_code == HTTP_200_OK
        assert Task.objects.count() == 1
        assert Task.objects.first().title == "New title"
        assert Task.objects.first().author == user
        assert Task.objects.first().project == project

    @pytest.mark.django_db
    def test_task_update_view_invalid_form(
        self, client: Client, user: User, task: Task, form_data: dict
    ):
        client.force_login(user)
        form_data["title"] = ""
        url = reverse("tasks:update", kwargs={"pk": task.pk})
        response = client.post(url, form_data, follow=True)

        assert response.status_code == HTTP_422_UNPROCESSABLE_ENTITY
        assert Task.objects.count() == 1
        assert response.templates[0].name == "tasks/task_form.html"
        assert response.context["form"].errors
        assert response.context["form"].errors["title"] == ["This field is required."]

        messages = list(response.context["messages"])
        assert len(messages) == 1
        assert str(messages[0]) == "Invalid form"

    @pytest.mark.django_db
    def test_task_update_view_not_authenticated(self, client: Client, task: Task):
        response = client.get(reverse("tasks:update", kwargs={"pk": task.pk}))
        assert response.status_code == HTTP_302_REDIRECT
        assert response.url.startswith("/accounts/login/")


@pytest.mark.django_db
class TestTaskDeleteView:
    def test_task_delete_view_authenticated(
        self, client: Client, user: User, task: Task
    ):
        client.force_login(user)
        response = client.post(reverse("tasks:delete", kwargs={"pk": task.pk}))
        assert response.status_code == HTTP_302_REDIRECT
        assert response.url.startswith("/tasks/")
        assert Task.objects.count() == 0

        messages = list(response.context["messages"])
        assert len(messages) == 1
        assert str(messages[0]) == "Task(s) deleted successfully"

    @pytest.mark.django_db
    def test_task_delete_view_not_authenticated(self, client: Client, task: Task):
        response = client.post(reverse("tasks:delete", kwargs={"pk": task.pk}))
        assert response.status_code == HTTP_302_REDIRECT
        assert response.url.startswith("/accounts/login/")
