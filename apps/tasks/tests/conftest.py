import pytest
from apps.tasks.models import Task
from apps.accounts.models import User
from apps.projects.models import Project
from apps.comments.models import Comment
from django.utils import timezone
from datetime import timedelta

TASK_TITLE = "title"
TASK_STATUS = "in_progress"
TASK_DESCRIPTION = "description"
TASK_DEADLINE = timezone.now() + timedelta(days=10)


USER_FIRST_NAME = "John"
USER_LAST_NAME = "Doe"
USER_USERNAME = "john.doe"
USER_EMAIL = "john.doe@example.com"
USER_PASSWORD = "zootoR587"


HTTP_200_OK = 200
HTTP_302_REDIRECT = 302
HTTP_403_FORBIDDEN = 403
HTTP_422_UNPROCESSABLE_ENTITY = 422


@pytest.fixture(scope="function")
def user(db):
    return User.objects.create_user(
        first_name="John",
        last_name="Doe",
        username="john.doe",
        email="john.doe@example.com",
        password="zootoR587",
    )


@pytest.fixture(scope="function")
def inactive_user(db):
    return User.objects.create_user(
        first_name="Jane",
        last_name="Doe",
        username="jane.doe",
        email="jane.doe@example.com",
        password="zootoR587",
        is_active=False,
    )


@pytest.fixture(scope="function")
def project(db, user):
    project = Project.objects.create(
        title="Test Project",
        description="Project description",
        deadline=timezone.now(),
        author=user,
    )
    return project


@pytest.fixture(scope="function")
def task(db, user, project):
    task = Task.objects.create(
        title=TASK_TITLE,
        status=TASK_STATUS,
        description=TASK_DESCRIPTION,
        deadline=TASK_DEADLINE,
        project=project,
        author=user,
    )
    return task


@pytest.fixture(scope="function")
def form_data(project: Project, user: User):
    return {
        "title": TASK_TITLE,
        "status": TASK_STATUS,
        "description": TASK_DESCRIPTION,
        "deadline": TASK_DEADLINE,
        "author": user.pk,
        "project": project.pk,
        "assigned_to": [user.pk],
    }


@pytest.fixture(scope="function")
def comment(db, user: User, task: Task):
    return Comment.objects.create(
        content="Test comment",
        task=task,
        author=user,
    )
