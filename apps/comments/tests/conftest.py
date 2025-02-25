import pytest
from apps.tasks.models import Task
from apps.accounts.models import User
from apps.projects.models import Project
from django.utils import timezone
from ..models import Comment


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
def project(db, user):
    project = Project.objects.create(
        title="Test Project",
        description="Project description",
        deadline=timezone.now(),
        author=user,
    )
    project.members.add(user)
    return project


@pytest.fixture(scope="function")
def task(db, user, project):
    task = Task.objects.create(
        title="Test Task",
        description="Task description",
        deadline=timezone.now(),
        project=project,
        author=user,
    )
    task.assigned_to.add(user)
    return task


@pytest.fixture(scope="function")
def comment(db, user, task):
    return Comment.objects.create(content="Test comment", task=task, author=user)


@pytest.fixture
def task_without_comments(db, user, project):
    task = Task.objects.create(
        title="Task without comments",
        description="No comments task",
        deadline=timezone.now(),
        project=project,
        author=user,
    )
    task.assigned_to.add(user)
    return task
