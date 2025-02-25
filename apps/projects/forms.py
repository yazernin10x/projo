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

    description = forms.CharField(
        required=False, widget=forms.Textarea(attrs={"placeholder": "Optionnel"})
    )


class ProjectMemberForm(forms.ModelForm):
    class Meta:
        model = ProjectMember
        fields = ["user", "role"]
        widgets = {
            "role": forms.Select(choices=ProjectMember.Role.choices),
        }

    # comment et où exclus l'utilisateur connecté
    user = forms.ModelChoiceField(queryset=User.objects.all())


class BaseProjectMemberFormSet(forms.BaseInlineFormSet):
    def clean(self):
        super().clean()

        for form in self.forms:
            if not form.cleaned_data.get("user"):
                form.add_error("user", "Veuillez sélectionner un utilisateur")

            if not form.cleaned_data.get("role"):
                form.add_error("role", "Veuillez sélectionner un rôle")


ProjectMemberFormSet = forms.inlineformset_factory(
    parent_model=Project,
    model=ProjectMember,
    form=ProjectMemberForm,
    formset=BaseProjectMemberFormSet,
    extra=0,
)
