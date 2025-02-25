import pytest
from apps.tasks.models import Task
from apps.projects.models import Project
from apps.accounts.models import User
from apps.tasks.tests.conftest import (
    TASK_TITLE,
    TASK_STATUS,
    TASK_DESCRIPTION,
    TASK_DEADLINE,
)


@pytest.mark.django_db
class TestTaskModel:
    def test_create(self, user: User, project: Project, task: Task):
        assert task.pk is not None
        assert task.title == TASK_TITLE
        assert task.status == TASK_STATUS
        assert task.description == TASK_DESCRIPTION
        assert task.deadline == TASK_DEADLINE
        assert task.project == project
        assert task.author == user
        assert Task.objects.count() == 1

    def test__str__(self, project: Project, task: Task):
        expected_str = (
            f"Task: {TASK_TITLE} "
            f"(Status: {TASK_STATUS}, "
            f"Project: {project.title})"
        )
        assert str(task) == expected_str

    def test__repr__(self, project: Project, task: Task):
        expected_repr = (
            f"<Task id={task.pk}, "
            f"title={TASK_TITLE!r}, "
            f"status={TASK_STATUS!r}, "
            f"project_id={project.pk}>"
        )
        assert repr(task) == expected_repr

    def test_assigned_to_users(self, user: User, task: Task):
        task.assigned_to.add(user)
        assert task.assigned_to.count() == 1
        assert user in task.assigned_to.all()
