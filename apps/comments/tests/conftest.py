import pytest
from apps.tasks.models import Task

from apps.core.tests.fixtures import (
    user_1,
    user_1_connected,
    user_2,
    user_2_connected,
    task,
    project,
    comment,
)


@pytest.fixture(scope="function")
def task_without_comments(db, user_1, user_2, project):
    task_ = Task.objects.create(
        title="Task without comments",
        description="No comments task",
        project=project,
        author=user_1,
    )
    task_.assigned_to.add(user_2)
    return task_
