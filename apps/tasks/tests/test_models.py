import pytest
from apps.tasks.models import Task
from apps.projects.models import Project
from apps.accounts.models import User
from apps.core.constants import TASK_TITLE, TASK_STATUS


@pytest.mark.django_db
class TestTaskModel:
    def test_create(
        self, user_1_connected: User, user_2: User, project: Project, task: Task
    ):
        assert task.pk is not None
        assert task.title == TASK_TITLE
        assert task.status == TASK_STATUS
        assert task.project == project
        assert task.author == user_1_connected
        assert task.assigned_to.count() == 1
        assert user_2 in task.assigned_to.all()
        assert Task.objects.count() == 1

    def test__str__(self, task: Task):
        assert str(task) == f"{TASK_TITLE} ({TASK_STATUS})"

    def test__repr__(self, task: Task):
        assert repr(task) == f"Task(id={task.pk}, title={TASK_TITLE!r})"
