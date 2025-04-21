from apps.projects.forms import ProjectForm, ProjectMemberForm, ProjectMemberFormSet
from apps.accounts.models import User
from apps.projects.models import Project
from apps.core.constants import (
    PROJECT_TITLE,
    PROJECT_DESCRIPTION,
    PROJECT_DEADLINE,
    PROJECT_MEMBER_ROLE,
)
import pytest
from apps.projects.models import ProjectMember


class TestProjetForm:
    def test_project_form_valid(self, project_form_data: dict):
        form = ProjectForm(data=project_form_data)
        assert form.is_valid()
        assert form.cleaned_data["title"] == PROJECT_TITLE
        assert form.cleaned_data["description"] == PROJECT_DESCRIPTION
        assert form.cleaned_data["deadline"] == PROJECT_DEADLINE

    def test_project_form_invalid(self):
        form = ProjectForm(data={"title": ""})
        assert not form.is_valid()
        assert "title" in form.errors
        assert form.errors["title"] == ["Ce champ est obligatoire."]


@pytest.mark.django_db
class TestProjectMemberForm:
    def test_form_initialization(self, users: dict[str, User], project: Project):
        form = ProjectMemberForm(user=users["user_1"], project=project)

        # Vérifie que le queryset exclut l'utilisateur courant et les superusers
        assert users["user_1"] not in form.fields["user"].queryset
        assert users["superuser"] not in form.fields["user"].queryset
        assert users["user_2"] in form.fields["user"].queryset

    def test_label_from_instance(self, users: dict[str, User], project: Project):
        """Test que le label affiche correctement le nom complet ou le username"""
        form = ProjectMemberForm(user=users["user_1"], project=project)

        # Test avec un utilisateur ayant un nom complet
        assert form.fields["user"].label_from_instance(users["user_1"]) == "John Doe"

        # Test avec un utilisateur n'ayant pas de nom complet
        assert form.fields["user"].label_from_instance(users["user_3"]) == "user_3"

    @pytest.mark.parametrize(
        "test_data,expected_valid",
        [
            # Cas valide
            (
                {
                    "user": lambda users: users["user_2"].pk,
                    "role": ProjectMember.Role.MEMBER.value,
                },
                True,
            ),
            # Cas invalide - utilisateur manquant
            ({"user": "", "role": ProjectMember.Role.MEMBER.value}, False),
            # Cas invalide - rôle manquant
            ({"user": lambda users: users["user_2"].pk, "role": ""}, False),
        ],
    )
    def test_form_validation(self, users, project, test_data, expected_valid):
        """Test la validation du formulaire avec différents scénarios"""
        # Résolution des valeurs lambda si présentes
        data = {
            key: value(users) if callable(value) else value
            for key, value in test_data.items()
        }

        form = ProjectMemberForm(data=data, user=users["user_1"], project=project)
        assert form.is_valid() == expected_valid

        if not expected_valid and data["user"] == "":
            assert "Ce champ est obligatoire." in form.errors.get("user", [])


@pytest.mark.django_db
class TestProjectMemberFormSet:
    def test_formset_initialization(self, users: dict[str, User], project: Project):
        """Test l'initialisation du formset"""
        formset = ProjectMemberFormSet(
            data=None,
            instance=None,
            form_kwargs={"user": users["user_1"], "project": project},
            prefix="project-members",
        )
        assert len(formset.forms) == 0

    @pytest.mark.parametrize(
        "member_data,expected_valid",
        [
            # Cas valide
            (
                {
                    "user": lambda users: str(users["user_2"].pk),
                    "role": PROJECT_MEMBER_ROLE,
                },
                True,
            ),
            # Cas invalide - utilisateur manquant
            ({"user": "", "role": PROJECT_MEMBER_ROLE}, False),
        ],
    )
    def test_formset_validation(
        self, users, project, formset_data, member_data, expected_valid
    ):
        """Test la validation du formset avec différents scénarios"""
        # Résolution des valeurs lambda si présentes
        data = {
            f"project-members-0-{key}": value(users) if callable(value) else value
            for key, value in member_data.items()
        }
        formset_data.update(data)
        formset = ProjectMemberFormSet(
            data=formset_data,
            instance=project,
            form_kwargs={"user": users["user_1"], "project": project},
            prefix="project-members",
        )
        formset.is_valid()
        assert formset.is_valid() == expected_valid

        if not expected_valid and data["project-members-0-user"] == "":
            assert "Ce champ est obligatoire." in formset.forms[0].errors.get(
                "user", []
            )

    def test_formset_multiple_members(self, users: dict[str, User], project: Project):
        """Test l'ajout de plusieurs membres dans le formset"""
        data = {
            "project-members-TOTAL_FORMS": "2",
            "project-members-INITIAL_FORMS": "0",
            "project-members-MIN_NUM_FORMS": "0",
            "project-members-MAX_NUM_FORMS": "1000",
            "project-members-0-user": str(users["user_2"].pk),
            "project-members-0-role": ProjectMember.Role.MEMBER,
            "project-members-0-project": str(project.id),
            "project-members-1-user": "",
            "project-members-1-role": ProjectMember.Role.MEMBER,
            "project-members-1-project": str(project.id),
        }

        formset = ProjectMemberFormSet(
            data=data,
            instance=project,
            form_kwargs={"user": users["user_1"], "project": project},
            prefix="project-members",
        )

        assert not formset.is_valid()
        assert "Ce champ est obligatoire." in formset.forms[1].errors.get("user", [])
