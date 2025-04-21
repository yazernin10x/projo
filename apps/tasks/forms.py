from django import forms
from .models import Task
from apps.accounts.models import User


class TaskForm(forms.ModelForm):
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
            "assigned_to": forms.SelectMultiple(),
        }

    # supprimer les user deja ajouter

    def __init__(self, *args, user=None, project=None, **kwargs):
        self.user = user
        self.project = project
        super().__init__(*args, **kwargs)
        if user and project:
            users = User.objects.exclude(pk=user.pk).exclude(is_superuser=True)
            users_pks = [
                user.pk for user in users if user in self.project.members.all()
            ]
            self.fields["assigned_to"].queryset = User.objects.filter(pk__in=users_pks)
            self.fields["assigned_to"].label_from_instance = (
                lambda user: user.get_full_name() or user.username
            )
