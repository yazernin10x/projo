import pytest
from django.utils import timezone
from apps.projects.models import Project, ProjectMember
from apps.accounts.models import User
from apps.core.constants import (
    PROJECT_TITLE,
    PROJECT_DESCRIPTION,
    PROJECT_MEMBER_ROLE,
)


@pytest.mark.django_db(transaction=True)
class TestProjectModel:
    def test_creation(self, project):
        assert project.title == PROJECT_TITLE
        assert project.description == PROJECT_DESCRIPTION
        assert project.deadline > timezone.now()
        assert project.created_at is not None
        assert project.updated_at is not None

    def test__str__(self, project):
        assert str(project) == f"{PROJECT_TITLE} - {project.author.username}"

    def test__repr__(self, project):
        id = project.id
        author = project.author.username
        assert (
            repr(project) == f"Project(id={id}, title={PROJECT_TITLE}, author={author})"
        )

    def test_get_members_with_data(self, user_2: User, project: Project):
        users = project.get_members_with_data()
        assert len(users) == 1
        assert users[0] == user_2
        assert users[0].joined_at is not None


@pytest.mark.django_db(transaction=True)
class TestProjectMemberModel:
    def test_creation(self, user_1: User, project_member: ProjectMember):
        assert project_member.user.username == user_1.username
        assert project_member.project.title == PROJECT_TITLE
        assert project_member.role == PROJECT_MEMBER_ROLE
        assert project_member.joined_at is not None

    def test_relation(self, project_form_data, user_2: User):
        project = Project.objects.create(**project_form_data)
        project.members.add(user_2)
        assert user_2.projects.count() == 1
        assert project.members.count() == 1

    def test__str__(self, project_member: ProjectMember):
        username = project_member.user.username
        project_title = project_member.project.title
        role = project_member.role
        assert str(project_member) == f"{username} - {project_title} ({role})"

    def test__repr__(self, project_member: ProjectMember):
        project_member.refresh_from_db()
        id = project_member.id
        username = project_member.user.username
        project_title = project_member.project.title
        role = project_member.role
        assert (
            repr(project_member)
            == f"ProjectMember(id={id}, user={username!r}, project={project_title!r}, role={role!r})"
        )

    def test_get_user_role(
        self, user_1: User, project: Project, project_member: ProjectMember
    ):
        role = ProjectMember.get_user_role(user_1, project)
        assert role == PROJECT_MEMBER_ROLE

    def test_get_user_role_none(self, user_1: User, project: Project):
        role = ProjectMember.get_user_role(user_1, project)
        assert role is None
