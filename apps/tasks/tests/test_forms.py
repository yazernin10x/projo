import pytest
from apps.tasks.forms import TaskForm
from apps.accounts.models import User
from apps.projects.models import Project
from apps.core.constants import TASK_TITLE, TASK_STATUS


@pytest.mark.django_db
class TestTaskForm:
    def test_valid_form(
        self, user_1_connected: User, user_2: User, form_data: dict, project: Project
    ):
        form_data["assigned_to"] = [user_2.pk]
        form = TaskForm(
            data=form_data,
            user=user_1_connected,
            project=project,
        )
        assert form.is_valid()
        assert form.cleaned_data["title"] == TASK_TITLE
        assert form.cleaned_data["status"] == TASK_STATUS
        assert form.cleaned_data["assigned_to"].first() == user_2

    def test_invalid_form(self, user_1_connected: User, project: Project):
        form = TaskForm(
            data={},
            user=user_1_connected,
            project=project,
        )
        assert not form.is_valid()
        assert "title" in form.errors
