import pytest
from django.test import Client

from apps.tasks.models import Task
from apps.projects.models import Project, ProjectMember
from apps.accounts.models import User
from apps.comments.models import Comment
from apps.core.constants import (
    PROJECT_TITLE,
    PROJECT_DESCRIPTION,
    PROJECT_DEADLINE,
    TASK_TITLE,
    TASK_STATUS,
    FIRST_NAME_1,
    LAST_NAME_1,
    USERNAME_1,
    PHONE_NUMBER_1,
    EMAIL_1,
    PASSWORD_1,
    COMMENT_CONTENT,
    FIRST_NAME_2,
    LAST_NAME_2,
    USERNAME_2,
    PHONE_NUMBER_2,
    EMAIL_2,
    PASSWORD_2,
)


@pytest.fixture(scope="function")
def user_1(db):
    return User.objects.create_user(
        first_name=FIRST_NAME_1,
        last_name=LAST_NAME_1,
        username=USERNAME_1,
        phone_number=PHONE_NUMBER_1,
        email=EMAIL_1,
        password=PASSWORD_1,
    )


@pytest.fixture(scope="function")
def user_1_connected(db, client: Client, user_1: User):
    client.force_login(user_1)
    return user_1


@pytest.fixture(scope="function")
def user_2(db):
    return User.objects.create_user(
        first_name=FIRST_NAME_2,
        last_name=LAST_NAME_2,
        username=USERNAME_2,
        phone_number=PHONE_NUMBER_2,
        email=EMAIL_2,
        password=PASSWORD_2,
    )


@pytest.fixture(scope="function")
def user_2_connected(db, client: Client, user_2: User):
    client.force_login(user_2)
    return user_2


@pytest.fixture(scope="function")
def project(db, user_1: User, user_2: User):
    project = Project.objects.create(
        title=PROJECT_TITLE,
        description=PROJECT_DESCRIPTION,
        deadline=PROJECT_DEADLINE,
        author=user_1,
    )

    ProjectMember.objects.create(
        project=project,
        user=user_2,
    )

    return project


@pytest.fixture(scope="function")
def task(db, user_1: User, user_2: User, project: Project):
    task = Task.objects.create(
        title=TASK_TITLE,
        status=TASK_STATUS,
        project=project,
        author=user_1,
    )

    task.assigned_to.through.objects.create(
        task=task,
        user=user_2,
    )
    return task


@pytest.fixture(scope="function")
def comment(db, user_1: User, task: Task):
    return Comment.objects.create(content=COMMENT_CONTENT, task=task, author=user_1)


@pytest.fixture
def superuser():
    return User.objects.create_superuser(
        username="admin", email="admin@test.com", password="password"
    )


@pytest.fixture
def moderator():
    return User.objects.create_user(
        username="moderator", email="moderator@test.com", password="password"
    )


@pytest.fixture
def project_with_moderator(project, moderator):
    ProjectMember.objects.create(project=project, user=moderator, role="moderator")
    return project


@pytest.fixture
def unauthorized_user():
    return User.objects.create_user(
        username="unauthorized", email="unauthorized@test.com", password="password"
    )
