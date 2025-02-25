from datetime import datetime, timezone
from http import HTTPStatus

import pytest
from django.urls import reverse
from django.test import Client
from django.contrib.messages import get_messages

from ..models import Project, ProjectMember
from apps.accounts.models import User

from .conftest import USERNAME, USER_PASSWORD

HTTP_200_OK = HTTPStatus.OK
HTTP_302_REDIRECT = HTTPStatus.FOUND
HTTP_404_NOT_FOUND = HTTPStatus.NOT_FOUND
HTTP_422_UNPROCESSABLE_ENTITY = HTTPStatus.UNPROCESSABLE_ENTITY


@pytest.mark.django_db
class TestProjectListView:
    def test_page_success(self, client: Client, user: User):
        client.force_login(user)
        response = client.get(reverse("projects:list"))
        assert response.status_code == HTTP_200_OK
        templates = [template.name for template in response.templates]
        assert "projects/list.html" in templates

    def test_context(self, client: Client, user: User, project: Project):
        client.force_login(user)
        response = client.get(reverse("projects:list"))
        assert response.status_code == HTTP_200_OK
        assert "projects" in response.context
        projects = response.context["projects"]
        assert len(projects) == 1
        assert project in projects


@pytest.mark.django_db
class TestProjectDetailView:
    def test_page_success(self, client: Client, project: Project):
        client.login(username=USERNAME, password=USER_PASSWORD)
        response = client.get(reverse("projects:detail", kwargs={"pk": project.pk}))
        assert response.status_code == HTTP_200_OK
        templates = [template.name for template in response.templates]
        assert "projects/detail.html" in templates

    def test_context(self, client: Client, user: User, project: Project):
        client.login(username=USERNAME, password=USER_PASSWORD)

        project.members.add(user)
        response = client.get(reverse("projects:detail", kwargs={"pk": project.pk}))
        assert response.status_code == HTTP_200_OK

        assert "project" in response.context
        assert project == response.context["project"]

        assert "project_members" in response.context
        project_members = response.context["project_members"]
        assert len(project_members) == 1
        assert project.members.first() == project_members.first().user


@pytest.mark.django_db
class TestProjectCreateView:
    def test_page_success(self, client: Client, user: User):
        client.force_login(user)
        response = client.get(reverse("projects:create"))
        assert response.status_code == HTTP_200_OK
        templates = [template.name for template in response.templates]
        assert "projects/project_form.html" in templates

    def test_form_valid(self, client: Client, project_form_data: dict):
        client.login(username=USERNAME, password=USER_PASSWORD)
        del project_form_data["author"]
        response = client.post(reverse("projects:create"), data=project_form_data)
        assert response.status_code == HTTP_302_REDIRECT
        assert Project.objects.count() == 1
        assert Project.objects.first().title == "Test Project"
        assert Project.objects.first().author == response.wsgi_request.user

        messages = list(get_messages(response.wsgi_request))
        assert len(messages) == 1
        assert messages[0].level_tag == "success"
        assert messages[0].message == "Project created successfully."

    def test_form_invalid(self, client: Client, user: User):
        client.force_login(user)
        response = client.post(reverse("projects:create"), {"title": ""})
        assert response.status_code == HTTP_422_UNPROCESSABLE_ENTITY
        assert Project.objects.count() == 0
        assert "projects/project_form.html" in [
            template.name for template in response.templates
        ]
        messages = list(get_messages(response.wsgi_request))
        assert len(messages) == 1
        assert messages[0].level_tag == "error"
        assert messages[0].message == "Please correct the errors below."


@pytest.mark.django_db
class TestProjectUpdateView:
    def test_page_success(self, client: Client, user: User, project: Project):
        client.force_login(user)
        response = client.get(reverse("projects:update", kwargs={"pk": project.pk}))
        assert response.status_code == HTTP_200_OK
        templates = [template.name for template in response.templates]
        assert "projects/project_form.html" in templates

    def test_form_valid(self, client: Client, project: Project):
        client.login(username=USERNAME, password=USER_PASSWORD)
        response = client.post(
            reverse("projects:update", kwargs={"pk": project.pk}),
            data={"title": "Test Project", "deadline": datetime(2025, 1, 1, 0, 0)},
        )
        assert response.status_code == HTTP_302_REDIRECT
        assert Project.objects.count() == 1
        assert Project.objects.first().title == "Test Project"
        assert Project.objects.first().deadline == datetime(
            2025, 1, 1, 0, 0, tzinfo=timezone.utc
        )
        assert Project.objects.first().author == response.wsgi_request.user

        messages = list(get_messages(response.wsgi_request))
        assert len(messages) == 1
        assert messages[0].level_tag == "success"
        assert messages[0].message == "Project updated successfully."

    def test_form_invalid(self, client: Client, project: Project):
        client.login(username=USERNAME, password=USER_PASSWORD)
        response = client.post(
            reverse("projects:update", kwargs={"pk": project.pk}), {"title": ""}
        )
        assert response.status_code == HTTP_422_UNPROCESSABLE_ENTITY
        assert "projects/project_form.html" in [
            template.name for template in response.templates
        ]

        messages = list(get_messages(response.wsgi_request))
        assert len(messages) == 1
        assert messages[0].level_tag == "error"
        assert messages[0].message == "Please correct the errors below."


@pytest.mark.django_db
class TestCreateMembersView:
    def test_redirect_if_not_logged_in(self, client, project: Project):
        url = reverse("projects:add_members", kwargs={"pk": project.pk})
        response = client.get(url)
        assert response.status_code == HTTP_302_REDIRECT
        url_redirect = reverse("accounts:login") + f"?next={url}"
        assert response.headers["Location"] == url_redirect

    def test_access_form_if_logged_in(self, client, project: Project):
        client.login(username=USERNAME, password=USER_PASSWORD)
        url = reverse("projects:add_members", kwargs={"pk": project.pk})
        response = client.get(url)

        assert response.status_code == HTTP_200_OK
        assert "formset" in response.context
        assert "project" in response.context
        assert project == response.context["project"]
        templates = [template.name for template in response.templates]
        assert "projects/project_members_form.html" in templates

    def test_add_member_valid_form(self, client: Client, project: Project):
        client.login(username=USERNAME, password=USER_PASSWORD)

        user = User.objects.create_user(
            first_name="test",
            last_name="user",
            username="testuser",
            email="testuser@example.com",
            password="password",
        )

        url = reverse("projects:add_members", kwargs={"pk": project.pk})
        response = client.post(
            url,
            data={
                "projectmember_set-0-user": user.pk,
                "projectmember_set-0-role": "member",
                "projectmember_set-TOTAL_FORMS": "1",
                "projectmember_set-INITIAL_FORMS": "0",
            },
        )

        assert response.status_code == HTTP_302_REDIRECT
        assert ProjectMember.objects.filter(project=project, user=user).exists()
        url_redirect = reverse("projects:detail", kwargs={"pk": project.pk})
        assert response.headers["Location"] == url_redirect

        messages = list(get_messages(response.wsgi_request))
        assert len(messages) == 1
        assert messages[0].level_tag == "success"
        assert messages[0].message == "Members added successfully."

    def test_add_member_invalid_form(self, client: Client, project: Project):
        client.login(username=USERNAME, password=USER_PASSWORD)
        url = reverse("projects:add_members", kwargs={"pk": project.pk})

        response = client.post(
            url,
            data={
                "projectmember_set-0-user": "",
                "projectmember_set-0-role": "",
                "projectmember_set-TOTAL_FORMS": "1",
                "projectmember_set-INITIAL_FORMS": "0",
            },
        )

        assert response.status_code == HTTP_422_UNPROCESSABLE_ENTITY
        assert ProjectMember.objects.count() == 0
        assert "projects/project_members_form.html" in [
            template.name for template in response.templates
        ]

        messages = list(get_messages(response.wsgi_request))
        assert len(messages) == 1
        assert messages[0].level_tag == "error"
        assert messages[0].message == "Please correct the errors below."
