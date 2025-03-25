import pytest
from django.utils import timezone
from ..models import Project, ProjectMember
from .conftest import (
    PROJECT_TITLE,
    PROJECT_DESCRIPTION,
    PROJECT_DEADLINE,
    USER_USERNAME,
    PROJECT_MEMBER_ROLE,
)
from django.core.exceptions import ValidationError


class TestProjectModel:
    def test_creation(self, project):
        assert project.title == PROJECT_TITLE
        assert project.description == PROJECT_DESCRIPTION
        assert project.deadline > timezone.now()
        assert project.created_at is not None
        assert project.updated_at is not None

    def test__str__(self, project):
        assert str(project) == f"{PROJECT_TITLE} - {USER_USERNAME}"

    def test__repr__(self, project):
        id = project.id
        assert (
            repr(project)
            == f"Project(id={id}, title={PROJECT_TITLE}, author={USER_USERNAME})"
        )


class TestProjectMemberModel:
    def test_creation(self, project_member):
        assert project_member.user.username == USER_USERNAME
        assert project_member.project.title == PROJECT_TITLE
        assert project_member.role == PROJECT_MEMBER_ROLE
        assert project_member.joined_at is not None

    def test_relation(self, project_form_data, user):
        project = Project.objects.create(**project_form_data)
        project.members.add(user)
        assert user.projects.count() == 1
        assert project.members.count() == 1

    def test_project_member_non_valid_role(self, project_member):
        with pytest.raises(ValidationError):
            project_member.role = "invalid_role"
            project_member.save()

    def test_optional_fields(self, project_member):
        project_no_description = Project.objects.create(
            title=PROJECT_TITLE,
            deadline=PROJECT_DEADLINE,
            author=project_member.user,
        )
        assert project_no_description.description is None
        assert project_no_description.members.count() == 0
