import pytest
from apps.tasks.models import Task
from apps.accounts.models import User
from apps.projects.models import Project, ProjectMember
from django.utils import timezone
from datetime import timedelta

PROJECT_TITLE = "Test Project"
PROJECT_DESCRIPTION = "A project description"
PROJECT_DEADLINE = timezone.now() + timedelta(days=7)

PROJECT_MEMBER_ROLE = "admin"

USER_FIRST_NAME = "John"
USER_LAST_NAME = "Doe"
USERNAME = "john.doe"
USER_EMAIL = "john.doe@example.com"
USER_PASSWORD = "zootoR587"


@pytest.fixture(scope="function")
def user(db):
    return User.objects.create_user(
        first_name=USER_FIRST_NAME,
        last_name=USER_LAST_NAME,
        username=USERNAME,
        email=USER_EMAIL,
        password=USER_PASSWORD,
    )


@pytest.fixture(scope="function")
def project_form_data(user: User):
    return {
        "title": PROJECT_TITLE,
        "description": PROJECT_DESCRIPTION,
        "deadline": PROJECT_DEADLINE,
        "author": user,
    }


@pytest.fixture(scope="function")
def project(db, user: User):
    proj = Project.objects.create(
        title=PROJECT_TITLE,
        description=PROJECT_DESCRIPTION,
        deadline=PROJECT_DEADLINE,
        author=user,
    )
    return proj


@pytest.fixture(scope="function")
def project_member_form_data(user: User, project: Project):
    return {
        "user": user,
        "project": project,
        "role": PROJECT_MEMBER_ROLE,
    }


@pytest.fixture
def project_member(user, project):
    return ProjectMember.objects.create(
        user=user,
        project=project,
        role=PROJECT_MEMBER_ROLE,
    )
