import pytest
from apps.tasks.forms import TaskCreateForm, TaskUpdateForm
from apps.projects.models import Project
from apps.accounts.models import User
from apps.tasks.tests.conftest import (
    TASK_TITLE,
    TASK_STATUS,
    TASK_DESCRIPTION,
    TASK_DEADLINE,
)


@pytest.mark.django_db
class TestTaskForm:
    def test_valid_form(self, user: User, project: Project, form_data: dict):
        form = TaskCreateForm(data=form_data)
        assert form.is_valid()
        assert form.cleaned_data["title"] == TASK_TITLE
        assert form.cleaned_data["status"] == TASK_STATUS
        assert form.cleaned_data["description"] == TASK_DESCRIPTION
        assert form.cleaned_data["deadline"] == TASK_DEADLINE
        assert form.cleaned_data["project"] == project
        assert form.cleaned_data["assigned_to"].first() == user

    def test_missing_required_fields(self):
        form = TaskCreateForm(data={})
        assert not form.is_valid()
        assert "title" in form.errors
        assert "project" in form.errors

    def test_deadline_optional(self, form_data: dict):
        del form_data["deadline"]
        form = TaskCreateForm(data=form_data)
        assert form.is_valid()
        assert form.cleaned_data["deadline"] is None

    def test_assigned_to_queryset(self, user: User, inactive_user: User):
        form = TaskCreateForm()
        assigned_to_queryset = form.fields["assigned_to"].queryset
        assert user in assigned_to_queryset
        assert inactive_user not in assigned_to_queryset


@pytest.mark.django_db
class TestTaskUpdateForm:
    def test_valid_form(self, user: User, project: Project, form_data: dict):
        del form_data["project"], form_data["author"]
        form_data["title"] = "New title"
        form = TaskUpdateForm(data=form_data)
        assert form.is_valid()
        assert form.cleaned_data["title"] == "New title"

    def test_invalid_form(self, form_data: dict):
        form = TaskUpdateForm(data=form_data)
        form.is_valid()
        assert not form.is_valid()
        assert "project" in form.errors
        assert "author" in form.errors
