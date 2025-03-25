from django import forms
from .models import Task
from apps.accounts.models import User


class TaskCreateForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = [
            "title",
            "description",
            "deadline",
            "status",
            "assigned_to",
        ]
        widgets = {
            "deadline": forms.DateTimeInput(attrs={"type": "datetime-local"}),
            "status": forms.Select(choices=Task.Status.choices),
            "assigned_to": forms.CheckboxSelectMultiple(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["assigned_to"].queryset = User.objects.filter(is_active=True)


class TaskUpdateForm(TaskCreateForm):
    class Meta(TaskCreateForm.Meta):
        pass
