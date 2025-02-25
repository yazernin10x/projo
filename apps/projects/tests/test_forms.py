import pytest
from ..forms import ProjectForm, ProjectMemberForm


class TestProjetForm:
    @pytest.mark.django_db
    def test_project_form_valid(self, project_form_data: dict):
        form = ProjectForm(data=project_form_data)
        assert form.is_valid()

    @pytest.mark.django_db
    def test_project_form_invalid(self, project_form_data: dict):
        project_form_data["title"] = ""
        form = ProjectForm(data=project_form_data)
        assert not form.is_valid()
        assert "title" in form.errors
        assert form.errors["title"] == ["This field is required."]


class TestProjectMemberForm:
    @pytest.mark.django_db
    def test_project_member_form_valid(self, project_member_form_data: dict):
        form = ProjectMemberForm(data=project_member_form_data)
        assert form.is_valid()

    @pytest.mark.django_db
    def test_project_member_form_invalid(self, project_member_form_data: dict):
        project_member_form_data["role"] = "invalid_role"
        form = ProjectMemberForm(data=project_member_form_data)
        assert not form.is_valid()
        assert "role" in form.errors
