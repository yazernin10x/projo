from datetime import datetime

import pytest
from django.urls import reverse
from django.test import Client

from apps.projects.models import Project, ProjectMember
from apps.accounts.models import User
from apps.tasks.models import Task

from apps.core.tests.helpers import assert_message_present

from apps.core.constants import (
    HTTP_200_OK,
    HTTP_302_REDIRECT,
    PROJECT_TITLE,
    HTTP_400_BAD_REQUEST,
    HTTP_403_FORBIDDEN,
)


@pytest.mark.django_db
class TestProjectListView:
    def test_page_success(
        self, client: Client, user_2_connected: User, project: Project
    ):
        response = client.get(reverse("projects:list"))
        assert response.status_code == HTTP_200_OK
        assert response.templates[0].name == "projects/list.html"

        assert "projects" in response.context
        assert len(response.context["projects"]) == 0

        assert "page_member_projects" in response.context
        page_member_projects = response.context["page_member_projects"]
        assert page_member_projects.number == 1
        assert len(page_member_projects.object_list) == 1
        assert project in page_member_projects.object_list

    def test_pagination(self, client: Client, user_1: User, user_2_connected: User):
        # Créer 15 projets où user_2 est membre
        ProjectMember.objects.all().delete()

        projects = []
        for i in range(15):
            project = Project.objects.create(
                title=f"Project {i}",
                description=f"Description {i}",
                author=user_1,
            )
            project.members.add(user_2_connected)
            projects.append(project)

        # Test première page
        response = client.get(reverse("projects:list"))
        assert response.status_code == HTTP_200_OK
        assert response.templates[0].name == "projects/list.html"

        page_member_projects = response.context["page_member_projects"]
        assert page_member_projects.number == 1
        assert len(page_member_projects.object_list) == 10  # paginate_by = 10
        assert all(
            [project in projects for project in list(page_member_projects.object_list)]
        )

        # Test deuxième page
        response = client.get(reverse("projects:list") + "?member_page=2")
        assert response.status_code == HTTP_200_OK
        assert response.templates[0].name == "projects/list.html"

        page_member_projects = response.context["page_member_projects"]
        assert page_member_projects.number == 2
        assert len(page_member_projects.object_list) == 5
        assert all(
            [project in projects for project in list(page_member_projects.object_list)]
        )


@pytest.mark.django_db
class TestProjectDetailView:
    def test_page_success(
        self, client: Client, user_2_connected: User, project: Project
    ):
        response = client.get(reverse("projects:detail", kwargs={"pk": project.pk}))
        assert response.status_code == HTTP_200_OK
        assert response.templates[0].name == "projects/detail.html"

        assert "project" in response.context
        assert project == response.context["project"]

        assert "page_project_members" in response.context
        page_project_members = response.context["page_project_members"]
        assert page_project_members.number == 1
        assert len(page_project_members.object_list) == 1
        assert project.members.first() == page_project_members.object_list[0]
        assert project.members.first() == user_2_connected

    def test_pagination_tasks(self, client, user_2_connected: User, project: Project):
        # Créer 8 tâches créées par user_2
        created_tasks = []
        for i in range(8):
            task = Task.objects.create(
                title=f"Created Task {i}",
                description=f"Description {i}",
                status="todo",
                project=project,
                author=user_2_connected,
                deadline=datetime(2024, 3, 20),
            )
            created_tasks.append(task)

        # Créer 7 tâches assignées à user_2
        assigned_tasks = []
        for i in range(7):
            task = Task.objects.create(
                title=f"Assigned Task {i}",
                description=f"Description {i}",
                status="todo",
                project=project,
                author=project.author,
                deadline=datetime(2024, 3, 20),
            )
            task.assigned_to.add(user_2_connected)
            task.save()
            assigned_tasks.append(task)

        # Test pagination des tâches créées
        response = client.get(reverse("projects:detail", kwargs={"pk": project.pk}))
        assert response.status_code == HTTP_200_OK
        assert response.templates[0].name == "projects/detail.html"

        page_created_tasks = response.context["page_created_tasks"]
        assert page_created_tasks.number == 1
        assert len(page_created_tasks.object_list) == 6  # tasks_per_page = 6
        assert all(
            [task in created_tasks for task in list(page_created_tasks.object_list)]
        )

        # Test deuxième page des tâches créées
        response = client.get(
            reverse("projects:detail", kwargs={"pk": project.pk}) + "?created_page=2"
        )
        page_created_tasks = response.context["page_created_tasks"]
        assert page_created_tasks.number == 2
        assert len(page_created_tasks.object_list) == 2
        assert all(
            [task in created_tasks for task in list(page_created_tasks.object_list)]
        )

        # Test pagination des tâches assignées
        response = client.get(reverse("projects:detail", kwargs={"pk": project.pk}))
        page_assigned_tasks = response.context["page_assigned_tasks"]
        assert page_assigned_tasks.number == 1
        assert len(page_assigned_tasks.object_list) == 6
        assert all(
            [task in assigned_tasks for task in list(page_assigned_tasks.object_list)]
        )

        # Test deuxième page des tâches assignées
        response = client.get(
            reverse("projects:detail", kwargs={"pk": project.pk}) + "?assigned_page=2"
        )
        page_assigned_tasks = response.context["page_assigned_tasks"]
        assert page_assigned_tasks.number == 2
        assert len(page_assigned_tasks.object_list) == 1
        assert all(
            [task in assigned_tasks for task in list(page_assigned_tasks.object_list)]
        )

    def test_pagination_members(self, client, user_2_connected: User, project: Project):
        # Supprimer les membres existants
        ProjectMember.objects.all().delete()

        # Créer 7 membres pour le projet
        members = []
        for i in range(7):
            user = User.objects.create(
                username=f"test_user_{i}",
                email=f"test{i}@example.com",
                password="testpass123",
            )
            project.members.add(user)
            members.append(user)

        # Test première page des membres
        response = client.get(reverse("projects:detail", kwargs={"pk": project.pk}))
        page_project_members = response.context["page_project_members"]
        assert page_project_members.number == 1
        assert len(page_project_members.object_list) == 5  # members_per_page = 5
        assert all(
            [member in members for member in list(page_project_members.object_list)]
        )

        # Test deuxième page des membres
        response = client.get(
            reverse("projects:detail", kwargs={"pk": project.pk}) + "?member_page=2"
        )
        page_project_members = response.context["page_project_members"]
        assert page_project_members.number == 2
        assert len(page_project_members.object_list) == 2
        assert all(
            [member in members for member in list(page_project_members.object_list)]
        )

    def test_task_filters(self, client, user_2_connected: User, project: Project):
        task1 = Task.objects.create(
            title="Task 1",
            description="Description 1",
            status="todo",
            project=project,
            author=user_2_connected,
            deadline=datetime(2024, 3, 20),
        )

        task2 = Task.objects.create(
            title="Task 2",
            description="Description 2",
            status="in_progress",
            project=project,
            author=user_2_connected,
            deadline=datetime(2024, 3, 21),
        )

        # Test filtre par statut
        url = reverse("projects:detail", kwargs={"pk": project.pk})
        response = client.get(url, {"status": "todo"})
        assert len(response.context["tasks"]) == 1
        assert response.context["tasks"][0].status == "todo"
        assert response.context["tasks"][0] == task1

        # Test filtre par deadline
        response = client.get(url, {"deadline": "2024-03-21"})
        assert len(response.context["tasks"]) == 1
        assert (
            response.context["tasks"][0].deadline.strftime("%Y-%m-%d") == "2024-03-21"
        )
        assert response.context["tasks"][0] == task2

        # Test combinaison des filtres
        response = client.get(url, {"status": "in_progress", "deadline": "2024-03-21"})
        assert len(response.context["tasks"]) == 1
        assert response.context["tasks"][0].status == "in_progress"
        assert (
            response.context["tasks"][0].deadline.strftime("%Y-%m-%d") == "2024-03-21"
        )
        assert response.context["tasks"][0] == task2


@pytest.mark.django_db
class TestProjectCreateView:
    def test_page_success(self, client: Client, user_1_connected: User):
        response = client.get(reverse("projects:create"))
        assert response.status_code == HTTP_200_OK
        assert response.templates[0].name == "projects/project_form.html"

    def test_form_valid(
        self,
        client: Client,
        user_1_connected: User,
        user_2: User,
        project_form_data: dict,
    ):
        response = client.post(reverse("projects:create"), data=project_form_data)
        assert response.status_code == HTTP_302_REDIRECT

        project = Project.objects.first()
        project.members.add(user_2)
        project.save()
        assert Project.objects.count() == 1
        assert project.title == PROJECT_TITLE
        assert project.author == user_1_connected
        assert project.members.first() == user_2
        url_redirect = reverse("projects:detail", kwargs={"pk": project.pk})
        assert response.headers["Location"] == url_redirect
        assert_message_present(response, "Projet créé avec succès.", "success")

    def test_form_invalid(self, client: Client, user_1_connected: User):
        response = client.post(reverse("projects:create"), {"title": ""})
        assert response.status_code == HTTP_200_OK
        assert Project.objects.count() == 0
        assert response.templates[0].name == "projects/project_form.html"


@pytest.mark.django_db
class TestProjectUpdateView:
    def test_page_success(
        self, client: Client, user_1_connected: User, project: Project
    ):
        response = client.get(reverse("projects:update", kwargs={"pk": project.pk}))
        assert response.status_code == HTTP_200_OK
        assert response.templates[0].name == "projects/project_form.html"
        assert project == response.context["project"]

    def test_form_valid(self, client: Client, user_1_connected: User, project: Project):
        url = reverse("projects:update", kwargs={"pk": project.pk})
        response = client.post(url, data={"title": "New test"})
        assert response.status_code == HTTP_302_REDIRECT
        assert Project.objects.first().title == "New test"

        url_redirect = reverse("projects:detail", kwargs={"pk": project.pk})
        assert response.headers["Location"] == url_redirect
        assert_message_present(response, "Projet mis à jour avec succès.", "success")

    def test_form_invalid(
        self, client: Client, user_1_connected: User, project: Project
    ):
        url = reverse("projects:update", kwargs={"pk": project.pk})
        response = client.post(url, {"title": ""})
        assert response.status_code == HTTP_200_OK
        assert response.context["project"] == project
        assert response.context["form"].errors == {
            "title": ["Ce champ est obligatoire."]
        }
        assert response.templates[0].name == "projects/project_form.html"


@pytest.mark.django_db
class TestProjectDeleteView:
    def test_delete(self, client: Client, user_1_connected: User, project: Project):
        url = reverse("projects:delete", kwargs={"pk": project.pk})
        response = client.post(url)
        assert response.status_code == HTTP_302_REDIRECT
        assert Project.objects.count() == 0
        url_redirect = reverse("projects:list")
        assert response.headers["Location"] == url_redirect
        assert_message_present(response, "Projet supprimé avec succès.", "success")


@pytest.mark.django_db
class TestManageMembersView:
    def test_access_form(self, client, user_1_connected: User, project: Project):
        url = reverse("projects:manage_members", kwargs={"pk": project.pk})
        response = client.get(url)

        assert response.status_code == HTTP_200_OK
        assert "project_members_formset" in response.context
        assert "project" in response.context
        assert project == response.context["project"]
        assert response.templates[0].name == "projects/project_members_form.html"

    def test_add_new_member(
        self, client: Client, user_1_connected: User, user_2: User, project: Project
    ):
        # Supprimer user_2 du projet pour le test
        project.members.remove(user_2)
        project.save()

        url = reverse("projects:manage_members", kwargs={"pk": project.pk})
        response = client.post(
            url,
            data={
                "project-members-TOTAL_FORMS": "1",
                "project-members-INITIAL_FORMS": "0",
                "project-members-0-user": user_2.pk,
                "project-members-0-role": "member",
                "project-members-0-id": "",
                "project-members-0-DELETE": "",
            },
        )

        assert response.status_code == HTTP_302_REDIRECT
        assert ProjectMember.objects.filter(project=project, user=user_2).exists()
        url_redirect = reverse("projects:detail", kwargs={"pk": project.pk})
        assert response.headers["Location"] == url_redirect
        assert_message_present(response, "Les modifications ont été enregistrées.")

    def test_update_existing_member(
        self, client: Client, user_1_connected: User, user_2: User, project: Project
    ):
        old_member = ProjectMember.objects.get(project=project, user=user_2)
        url = reverse("projects:manage_members", kwargs={"pk": project.pk})
        response = client.post(
            url,
            data={
                "project-members-TOTAL_FORMS": "1",
                "project-members-INITIAL_FORMS": "1",
                "project-members-0-user": user_2.pk,
                "project-members-0-role": "moderator",
                "project-members-0-id": old_member.pk,  # id of the member to update
                "project-members-0-DELETE": "",
                "project-members-0-project": project.pk,
            },
        )
        assert response.status_code == HTTP_302_REDIRECT
        url_redirect = reverse("projects:detail", kwargs={"pk": project.pk})
        assert response.headers["Location"] == url_redirect
        assert ProjectMember.objects.get(pk=old_member.pk).role == "moderator"
        assert_message_present(response, "Les modifications ont été enregistrées.")

    def test_remove_member(
        self, client: Client, user_1_connected: User, user_2: User, project: Project
    ):
        old_member = ProjectMember.objects.get(project=project, user=user_2)
        url = reverse("projects:manage_members", kwargs={"pk": project.pk})
        response = client.post(
            url,
            data={
                "project-members-TOTAL_FORMS": "1",
                "project-members-INITIAL_FORMS": "1",
                "project-members-0-user": user_2.pk,
                "project-members-0-role": "member",
                "project-members-0-DELETE": "on",
                "project-members-0-id": old_member.pk,  # id of the member to delete
                "project-members-0-project": project.pk,
            },
        )

        assert response.status_code == HTTP_302_REDIRECT
        assert ProjectMember.objects.filter(project=project, user=user_2).count() == 0
        url_redirect = reverse("projects:detail", kwargs={"pk": project.pk})
        assert response.headers["Location"] == url_redirect
        assert_message_present(response, "Les modifications ont été enregistrées.")

    def test_invalid_form(
        self, client: Client, user_1_connected: User, project: Project
    ):
        url = reverse("projects:manage_members", kwargs={"pk": project.pk})
        response = client.post(
            url,
            data={
                "project-members-0-user": "",
                "project-members-0-role": "",
                "project-members-TOTAL_FORMS": "1",
                "project-members-INITIAL_FORMS": "0",
            },
        )

        assert response.status_code == HTTP_200_OK
        assert response.context["project_members_formset"].errors[0] == {
            "user": ["Ce champ est obligatoire."],
            "role": ["Ce champ est obligatoire."],
        }
        assert response.templates[0].name == "projects/project_members_form.html"


@pytest.mark.django_db
class TestRemoveMemberView:
    def test_remove_member(
        self, client: Client, user_1_connected: User, user_2: User, project: Project
    ):
        url = reverse(
            "projects:remove_member",
            kwargs={"pk": project.pk, "member_pk": user_2.pk},
        )
        response = client.post(url)

        assert response.status_code == HTTP_302_REDIRECT
        assert ProjectMember.objects.filter(project=project, user=user_2).count() == 0
        url_redirect = reverse("projects:detail", kwargs={"pk": project.pk})
        assert response.headers["Location"] == url_redirect
        assert_message_present(response, "Membre retiré avec succès.")


@pytest.mark.django_db
class TestProjectStatusUpdate:
    def test_update_status_as_author(self, client, user_1_connected, project: Project):
        """Test la mise à jour du statut par un auteur"""
        response = client.post(
            reverse("projects:update_status", args=[project.pk]),
            {"status": Project.Status.IN_PROGRESS},
        )
        assert response.status_code == HTTP_200_OK
        project.refresh_from_db()
        assert project.status == Project.Status.IN_PROGRESS
        assert response.json()["status"] == "success"
        assert response.json()["project_status"] == "in_progress"
        assert response.json()["project_status_display"] == "En cours"

    def test_update_status_as_superuser(self, client, superuser, project):
        """Test la mise à jour du statut par un superuser"""
        client.login(username="admin", password="password")
        response = client.post(
            reverse("projects:update_status", args=[project.pk]),
            {"status": Project.Status.COMPLETED},
        )
        assert response.status_code == HTTP_200_OK
        project.refresh_from_db()
        assert project.status == Project.Status.COMPLETED
        assert response.json()["status"] == "success"
        assert response.json()["project_status"] == "completed"
        assert response.json()["project_status_display"] == "Terminé"

    def test_update_status_as_moderator(
        self, client, moderator, project_with_moderator
    ):
        """Test la mise à jour du statut par un modérateur"""
        client.login(username="moderator", password="password")
        response = client.post(
            reverse("projects:update_status", args=[project_with_moderator.pk]),
            {"status": Project.Status.IN_PROGRESS},
        )
        assert response.status_code == HTTP_200_OK
        project_with_moderator.refresh_from_db()
        assert project_with_moderator.status == Project.Status.IN_PROGRESS
        assert response.json()["status"] == "success"
        assert response.json()["project_status"] == "in_progress"
        assert response.json()["project_status_display"] == "En cours"

    def test_update_status_unauthorized(self, client, unauthorized_user, project):
        """Test la mise à jour du statut par un utilisateur non autorisé"""
        client.login(username="unauthorized", password="password")
        response = client.post(
            reverse("projects:update_status", args=[project.pk]),
            {"status": Project.Status.IN_PROGRESS},
        )
        assert response.status_code == HTTP_403_FORBIDDEN
        assert response.json()["status"] == "error"
        assert response.json()["message"] == "Permission refusée"

    def test_update_status_invalid_status(self, client, user_1_connected, project):
        """Test la mise à jour avec un statut invalide"""
        response = client.post(
            reverse("projects:update_status", args=[project.pk]),
            {"status": "INVALID_STATUS"},
        )
        assert response.status_code == HTTP_400_BAD_REQUEST
        assert response.json()["status"] == "error"
        assert response.json()["message"] == "Statut invalide"

    def test_update_status_unauthenticated(self, client, project):
        """Test la mise à jour par un utilisateur non authentifié"""
        response = client.post(
            reverse("projects:update_status", args=[project.pk]),
            {"status": Project.Status.IN_PROGRESS},
        )
        assert response.status_code == HTTP_302_REDIRECT
