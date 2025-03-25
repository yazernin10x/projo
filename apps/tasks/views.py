from django.contrib import messages
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import (
    DetailView,
    CreateView,
    UpdateView,
    DeleteView,
)

from apps.projects.models import Project, ProjectMember
from apps.tasks.tests.conftest import HTTP_422_UNPROCESSABLE_ENTITY

from .models import Task
from .forms import TaskCreateForm, TaskUpdateForm
from apps.comments.models import Comment
from apps.accounts.models import User
from apps.comments.forms import CommentForm


from django.shortcuts import render


def get_comment_create_form(request, task_pk):
    form = CommentForm()
    task = get_object_or_404(Task, pk=task_pk)
    context = {"form": form, "task": task}
    return render(request, "tasks/partials/comment_form_modal.html", context)


def get_comment_update_form(request, comment_pk):
    comment = get_object_or_404(Comment, pk=comment_pk)
    form = CommentForm(instance=comment)
    context = {"form": form, "comment": comment}
    return render(request, "tasks/partials/comment_form_modal.html", context)


class TaskDetailView(LoginRequiredMixin, DetailView):
    model = Task
    template_name = "tasks/detail.html"
    context_object_name = "task"

    def get_object(self):
        user = self.request.user
        if self.kwargs.get("owner_pk"):
            user = get_object_or_404(User, pk=self.kwargs["owner_pk"])

        return get_object_or_404(Task, pk=self.kwargs["pk"], author=user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        comments = Comment.objects.filter(task=self.object)
        context["comments"] = comments

        query_set = Task.objects.filter(assigned_to=self.request.user)
        assigned_tasks = query_set.order_by("-created_at")
        context["assigned_tasks"] = assigned_tasks

        project = self.object.project
        if project.members and self.kwargs.get("owner_pk"):
            context["user_role"] = (
                ProjectMember.objects.filter(user=self.request.user).first().role
            )
            print(context["user_role"])
        return context


class TaskCreateView(LoginRequiredMixin, CreateView):
    model = Task
    form_class = TaskCreateForm
    template_name = "tasks/task_form.html"

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.project = get_object_or_404(Project, pk=self.kwargs["project_pk"])
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "Invalid form")
        return super().form_invalid(form)

    def get_success_url(self) -> str:
        messages.success(self.request, "Task created successfully")
        return reverse_lazy("projects:detail", kwargs={"pk": self.object.project.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["project"] = get_object_or_404(Project, pk=self.kwargs["project_pk"])
        return context


class TaskUpdateView(LoginRequiredMixin, UpdateView):
    model = Task
    form_class = TaskUpdateForm
    template_name = "tasks/task_form.html"

    def form_valid(self, form):
        return super().form_valid(form)

    def form_invalid(self, form):
        response = super().form_invalid(form)
        response.status_code = HTTP_422_UNPROCESSABLE_ENTITY
        messages.error(self.request, "Invalid form")
        return response

    def get_success_url(self) -> str:
        messages.success(self.request, "Task updated successfully")
        return reverse_lazy("projects:detail", kwargs={"pk": self.object.project.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["project"] = get_object_or_404(Project, pk=self.object.project.pk)

        project = self.object.project
        if project.members and self.kwargs.get("owner_pk"):
            context["user_role"] = (
                ProjectMember.objects.filter(user=self.request.user).first().role
            )
            print(context["user_role"])
        return context


class TaskDeleteView(LoginRequiredMixin, DeleteView):
    model = Task

    def get_object(self):
        return get_object_or_404(Task, pk=self.kwargs["pk"], author=self.request.user)

    def get_success_url(self):
        messages.success(self.request, "Task(s) deleted successfully")
        return reverse_lazy("projects:detail", kwargs={"pk": self.object.project.pk})
