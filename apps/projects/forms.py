from django import forms
from .models import Project, ProjectMember
from apps.accounts.models import User


class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ["title", "description", "deadline"]
        widgets = {
            "deadline": forms.DateTimeInput(attrs={"type": "datetime-local"}),
        }


class ProjectMemberForm(forms.ModelForm):
    class Meta:
        model = ProjectMember
        fields = ["user", "role"]
        widgets = {
            "role": forms.Select(choices=ProjectMember.Role.choices),
        }

    user = forms.ModelChoiceField(
        queryset=User.objects.none(),
        required=True,
        error_messages={"invalid_choice": "Ce champ est obligatoire."},
    )

    def __init__(self, *args, user=None, project=None, **kwargs):
        self.user = user
        self.project = project
        # self.project = kwargs.pop("instance", None)  # Récupère le projet
        super().__init__(*args, **kwargs)

        if user and project:
            # users = User.objects.exclude(pk=self.user.pk).exclude(is_superuser=True)
            # users_pks = [
            #     user.pk for user in users if user not in self.project.members.all()
            # ]
            self.fields["user"].queryset = User.objects.all()
            self.fields["user"].label_from_instance = (
                lambda user: user.get_full_name() or user.username
            )


class BaseProjectMemberFormSet(forms.BaseInlineFormSet):
    deletion_widget: forms.HiddenInput = forms.HiddenInput()

    def __init__(self, *args, user=None, project=None, **kwargs):
        self.user = user
        self.project = project
        super().__init__(*args, **kwargs)

    def clean(self):
        super().clean()
        for form in self.forms:
            if not form.cleaned_data.get("user"):
                if "user" in form.errors:
                    del form.errors["user"]
                form.add_error("user", "Ce champ est obligatoire.")


ProjectMemberFormSet = forms.inlineformset_factory(
    parent_model=Project,
    model=ProjectMember,
    form=ProjectMemberForm,
    formset=BaseProjectMemberFormSet,
    extra=0,
    fields=["user", "role"],
)
