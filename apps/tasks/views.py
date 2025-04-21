from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.decorators.http import require_POST
from django.contrib.messages.views import SuccessMessageMixin
from django.views.generic import (
    DetailView,
    CreateView,
    UpdateView,
    DeleteView,
)
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required

from apps.projects.models import Project, ProjectMember
from apps.tasks.models import Task
from apps.tasks.forms import TaskForm
from apps.comments.models import Comment
from apps.core.constants import HTTP_403_FORBIDDEN, HTTP_400_BAD_REQUEST


class TaskDetailView(LoginRequiredMixin, DetailView):
    model = Task
    template_name = "tasks/detail.html"
    context_object_name = "task"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["comments"] = Comment.objects.filter(task=self.object)
        return context


class TaskCreateView(SuccessMessageMixin, LoginRequiredMixin, CreateView):
    model = Task
    form_class = TaskForm
    template_name = "tasks/task_form.html"
    success_message = "La tâche a été créée avec succès."

    def get_success_url(self):
        return reverse_lazy("tasks:detail", kwargs={"pk": self.object.pk})

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        kwargs["project"] = get_object_or_404(Project, pk=self.kwargs["project_pk"])
        return kwargs

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.project = get_object_or_404(Project, pk=self.kwargs["project_pk"])
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["project"] = get_object_or_404(Project, pk=self.kwargs["project_pk"])
        return context


class TaskUpdateView(SuccessMessageMixin, LoginRequiredMixin, UpdateView):
    model = Task
    form_class = TaskForm
    context_object_name = "task"
    template_name = "tasks/task_form.html"
    success_message = "La tâche a été modifiée avec succès."

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        kwargs["project"] = self.object.project
        return kwargs

    def get_success_url(self):
        return reverse_lazy("tasks:detail", kwargs={"pk": self.object.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["project"] = get_object_or_404(Project, pk=self.object.project.pk)
        return context


class TaskDeleteView(SuccessMessageMixin, LoginRequiredMixin, DeleteView):
    model = Task
    success_message = "La tâche a été supprimée avec succès."

    def get_success_url(self):
        return reverse_lazy("projects:detail", kwargs={"pk": self.object.project.pk})


@require_POST
@login_required
def update_task_status(request, pk):
    task = get_object_or_404(Task, pk=pk)

    if not (
        request.user.is_superuser
        or request.user == task.author
        or ProjectMember.objects.filter(
            user=request.user, project=task.project, role="moderator"
        ).exists()
    ):
        return JsonResponse(
            {"status": "error", "message": "Permission refusée"},
            status=HTTP_403_FORBIDDEN,
        )

    if request.method == "POST":
        new_status = request.POST.get("status")
        if new_status in dict(Task.Status.choices):
            task.status = new_status
            task.save()

            return JsonResponse(
                {
                    "status": "success",
                    "task_status": new_status,
                    "task_status_display": task.get_status_display(),
                }
            )

    return JsonResponse(
        {"status": "error", "message": "Statut invalide"},
        status=HTTP_400_BAD_REQUEST,
    )
