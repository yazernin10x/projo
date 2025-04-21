import pytest
from apps.accounts.models import User
from apps.projects.models import Project, ProjectMember
from apps.core.constants import (
    PROJECT_TITLE,
    PROJECT_DESCRIPTION,
    PROJECT_DEADLINE,
    PROJECT_MEMBER_ROLE,
)
from apps.core.tests.fixtures import (
    user_1,
    user_1_connected,
    user_2,
    user_2_connected,
    project,
    superuser,
    moderator,
    project_with_moderator,
    unauthorized_user,
)


@pytest.fixture
def users(user_1: User, user_2: User, superuser: User):
    """Fixture pour créer les utilisateurs de test"""
    return {
        "user_1": user_1,
        "user_2": user_2,
        "user_3": User.objects.create_user(
            username="user_3", email="user_3@test.com", password="password"
        ),
        "superuser": superuser,
    }


@pytest.fixture
def formset_data(project: Project):
    """Fixture pour les données de base du formset"""
    return {
        "project-members-TOTAL_FORMS": "1",
        "project-members-INITIAL_FORMS": "0",
        "project-members-0-id": "",
        "project-members-0-DELETE": "",
        "project-members-0-project": project.pk,
    }


@pytest.fixture(scope="function")
def project_form_data(user_1: User):
    return {
        "title": PROJECT_TITLE,
        "description": PROJECT_DESCRIPTION,
        "deadline": PROJECT_DEADLINE,
        "author": user_1,
    }


@pytest.fixture(scope="function")
def project_member_form_data(user_1: User, project: Project):
    return {
        "user": user_1,
        "project": project,
        "role": PROJECT_MEMBER_ROLE,
    }


@pytest.fixture
def project_member(user_1: User, project: Project):
    return ProjectMember.objects.create(
        user=user_1,
        project=project,
        role=PROJECT_MEMBER_ROLE,
    )
