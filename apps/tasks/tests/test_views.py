import pytest
from django.urls import reverse
from django.test import Client

from apps.comments.models import Comment
from apps.core.tests.helpers import assert_message_present
from apps.tasks.models import Task
from apps.accounts.models import User
from apps.projects.models import Project
from apps.core.constants import (
    HTTP_200_OK,
    HTTP_302_REDIRECT,
    TASK_TITLE,
    HTTP_403_FORBIDDEN,
    HTTP_400_BAD_REQUEST,
    HTTP_405_METHOD_NOT_ALLOWED,
)


@pytest.mark.django_db
class TestTaskDetailView:
    def test_page_access(
        self, client: Client, user_1_connected: User, task: Task, comment: Comment
    ):
        response = client.get(reverse("tasks:detail", kwargs={"pk": task.pk}))
        assert response.status_code == HTTP_200_OK
        assert response.templates[0].name == "tasks/detail.html"
        assert response.context["task"] == task
        assert response.context["comments"].count() == 1
        assert response.context["comments"][0] == comment


@pytest.mark.django_db
class TestTaskCreateView:
    def test_page_access(
        self, client: Client, user_1_connected: User, project: Project
    ):
        response = client.get(
            reverse("tasks:create", kwargs={"project_pk": project.pk})
        )
        assert response.status_code == HTTP_200_OK
        assert response.templates[0].name == "tasks/task_form.html"
        assert response.context["form"].errors == {}
        assert response.context["project"] == project

    def test_valid_submission(
        self,
        client: Client,
        user_1_connected: User,
        user_2: User,
        project: Project,
        form_data: dict,
    ):
        response = client.post(
            reverse("tasks:create", kwargs={"project_pk": project.pk}), form_data
        )
        assert response.status_code == HTTP_302_REDIRECT

        task = Task.objects.get(title=TASK_TITLE)
        task.assigned_to.add(user_2)
        task.save()
        assert task is not None
        assert response.headers["Location"] == reverse(
            "tasks:detail", kwargs={"pk": task.pk}
        )
        assert task.title == TASK_TITLE
        assert task.author == user_1_connected
        assert task.project == project
        assert task.assigned_to.count() == 1
        assert task.assigned_to.first() == user_2

        assert_message_present(response, "La tâche a été créée avec succès.")

    @pytest.mark.django_db
    def test_invalid_submission(
        self, client: Client, user_1_connected: User, project: Project
    ):
        url = reverse("tasks:create", kwargs={"project_pk": project.pk})
        response = client.post(url, {"title": ""})

        assert response.status_code == HTTP_200_OK
        assert Task.objects.count() == 0
        assert response.templates[0].name == "tasks/task_form.html"
        assert response.context["form"].errors["title"] == ["Ce champ est obligatoire."]


@pytest.mark.django_db
class TestTaskUpdateView:
    def test_page_access(self, client: Client, user_1_connected: User, task: Task):
        response = client.get(reverse("tasks:update", kwargs={"pk": task.pk}))
        assert response.status_code == HTTP_200_OK
        assert response.templates[0].name == "tasks/task_form.html"
        assert response.context["form"].errors == {}
        assert response.context["task"] == task
        assert response.context["project"] == task.project

    def test_valid_submission(
        self,
        client: Client,
        user_1_connected: User,
        user_2: User,
        task: Task,
        project: Project,
        form_data: dict,
    ):
        user_3 = User.objects.create_user(
            username="user_3", email="user_3@test.com", password="password"
        )
        form_data["title"] = "New title"
        url = reverse("tasks:update", kwargs={"pk": task.pk})
        response = client.post(url, form_data)

        assert response.status_code == HTTP_302_REDIRECT

        task = Task.objects.get(title=form_data["title"])
        task.assigned_to.add(user_3)
        task.save()

        assert task is not None
        assert response.headers["Location"] == reverse(
            "tasks:detail", kwargs={"pk": task.pk}
        )
        assert task.title == form_data["title"]
        assert task.author == user_1_connected
        assert task.project == project
        assert task.assigned_to.count() == 1
        assert task.assigned_to.first() == user_3
        assert_message_present(response, "La tâche a été modifiée avec succès.")

    @pytest.mark.django_db
    def test_invalid_submission(
        self, client: Client, user_1_connected: User, task: Task
    ):
        url = reverse("tasks:update", kwargs={"pk": task.pk})
        response = client.post(url, {"title": ""})
        assert response.status_code == HTTP_200_OK
        assert Task.objects.count() == 1
        assert response.templates[0].name == "tasks/task_form.html"
        assert response.context["form"].errors["title"] == ["Ce champ est obligatoire."]


@pytest.mark.django_db
class TestTaskDeleteView:
    def test_task_delete_view_authenticated(
        self, client: Client, user_1_connected: User, task: Task
    ):
        response = client.post(reverse("tasks:delete", kwargs={"pk": task.pk}))
        assert response.status_code == HTTP_302_REDIRECT
        assert response.headers["Location"] == reverse(
            "projects:detail", kwargs={"pk": task.project.pk}
        )
        assert not Task.objects.filter(pk=task.pk).exists()

        assert_message_present(response, "La tâche a été supprimée avec succès.")


@pytest.mark.django_db
class TestUpdateTaskStatus:
    def test_update_task_status_success(
        self, client: Client, user_1_connected: User, task: Task
    ):
        """Test la mise à jour réussie du statut d'une tâche"""
        new_status = "in_progress"
        response = client.post(
            reverse("tasks:update_status", kwargs={"pk": task.pk}),
            {"status": new_status},
        )

        assert response.status_code == HTTP_200_OK
        data = response.json()
        assert data["status"] == "success"
        assert data["task_status"] == new_status
        assert data["task_status_display"] == Task.Status(new_status).label

        # Vérifier que le statut a bien été mis à jour en base
        task.refresh_from_db()
        assert task.status == new_status

    def test_update_task_status_moderator(
        self, client: Client, moderator: User, task: Task, project: Project
    ):
        client.force_login(moderator)
        """Test la mise à jour par un modérateur du projet"""
        # Ajouter l'utilisateur comme modérateur du projet
        project.members.add(moderator, through_defaults={"role": "moderator"})
        project.save()

        new_status = "done"
        response = client.post(
            reverse("tasks:update_status", kwargs={"pk": task.pk}),
            {"status": new_status},
        )

        assert response.status_code == HTTP_200_OK
        data = response.json()
        assert data["status"] == "success"
        assert data["task_status"] == new_status
        assert data["task_status_display"] == Task.Status(new_status).label

    def test_update_task_status_superuser(
        self, client: Client, superuser: User, task: Task
    ):
        """Test la mise à jour par un superuser"""
        client.force_login(superuser)
        new_status = "in_progress"
        response = client.post(
            reverse("tasks:update_status", kwargs={"pk": task.pk}),
            {"status": new_status},
        )

        assert response.status_code == HTTP_200_OK
        data = response.json()
        assert data["status"] == "success"
        assert data["task_status"] == new_status
        assert data["task_status_display"] == Task.Status(new_status).label

    def test_update_task_status_permission_denied(
        self, client: Client, unauthorized_user: User, task: Task
    ):
        """Test le refus de mise à jour pour un utilisateur non autorisé"""
        client.force_login(unauthorized_user)
        response = client.post(
            reverse("tasks:update_status", kwargs={"pk": task.pk}),
            {"status": "in_progress"},
        )

        assert response.status_code == HTTP_403_FORBIDDEN
        data = response.json()
        assert data["status"] == "error"
        assert data["message"] == "Permission refusée"

    def test_update_task_status_invalid_status(
        self, client: Client, user_1_connected: User, task: Task
    ):
        """Test la soumission d'un statut invalide"""
        response = client.post(
            reverse("tasks:update_status", kwargs={"pk": task.pk}),
            {"status": "invalid_status"},
        )

        assert response.status_code == HTTP_400_BAD_REQUEST
        data = response.json()
        assert data["status"] == "error"
        assert data["message"] == "Statut invalide"

    @pytest.mark.parametrize("method", ["get", "put", "delete"])
    def test_update_task_status_wrong_method(
        self, client: Client, user_1_connected: User, task: Task, method
    ):
        request_method = getattr(client, method)
        response = request_method(
            reverse("tasks:update_status", kwargs={"pk": task.pk}),
            {"status": "completed"},
        )
        assert response.status_code == HTTP_405_METHOD_NOT_ALLOWED
