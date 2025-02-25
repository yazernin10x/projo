from django.forms import inlineformset_factory
from django.urls import reverse_lazy
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView,
)
from django.db.models import Prefetch, F

from apps.accounts.models import User

from .models import Project, ProjectMember
from .forms import ProjectForm, ProjectMemberForm, ProjectMemberFormSet
from apps.notifications.models import Notification

HTTP_422_UNPROCESSABLE_ENTITY = 422


class ProjectListView(LoginRequiredMixin, ListView):
    model = Project
    template_name = "projects/list.html"
    context_object_name = "projects"

    def get_queryset(self):
        return Project.objects.filter(author=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["member_projects"] = Project.objects.filter(members=self.request.user)
        return context


class ProjectDetailView(LoginRequiredMixin, DetailView):
    model = Project
    template_name = "projects/detail.html"
    context_object_name = "project"

    def get_queryset(self):
        return Project.objects.prefetch_related(
            Prefetch(
                "members",
                queryset=User.objects.annotate(member_role=F("project_members__role")),
            )
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["project_members"] = ProjectMember.objects.filter(project=self.object)
        return context


class ProjectCreateView(LoginRequiredMixin, CreateView):
    model = Project
    form_class = ProjectForm
    template_name = "projects/project_form.html"
    success_url = reverse_lazy("projects:list")

    def get_success_url(self):
        messages.success(self.request, "Project created successfully.")
        notification = Notification.objects.create(
            message="Un nouveau projet a été créé : " + self.object.title
        )
        notification.users.add(self.request.user)
        return reverse_lazy("projects:detail", kwargs={"pk": self.object.pk})

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "Please correct the errors below.")
        response = super().form_invalid(form)
        response.status_code = HTTP_422_UNPROCESSABLE_ENTITY
        return response


class ProjectUpdateView(LoginRequiredMixin, UpdateView):
    model = Project
    form_class = ProjectForm
    template_name = "projects/project_form.html"
    context_object_name = "project"

    def get_success_url(self):
        messages.success(self.request, "Project updated successfully.")
        return reverse_lazy("projects:detail", kwargs={"pk": self.object.pk})

    def form_valid(self, form):
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "Please correct the errors below.")
        response = super().form_invalid(form)
        response.status_code = HTTP_422_UNPROCESSABLE_ENTITY
        return response


class ProjectDeleteView(LoginRequiredMixin, DeleteView):
    model = Project
    success_message = "Project deleted successfully."

    def get_success_url(self):
        messages.success(self.request, self.success_message)
        return reverse_lazy("projects:list")


@login_required
def add_members(request, pk: int):
    project = get_object_or_404(Project, pk=pk)
    project_members_formset = ProjectMemberFormSet(
        request.POST or None, prefix="project-members", instance=project
    )

    if request.method == "POST":
        if project_members_formset.is_valid():
            project_members_formset.save()
            messages.success(request, "Members added successfully.")
            return redirect("projects:detail", pk=project.pk)
        else:
            print(project_members_formset.errors, "///////////////////////////////////")
            messages.error(request, "Please correct the errors below.")

    return render(request, "projects/project_members_form.html", locals())


@login_required
def remove_member(request, pk: int, member_id: int):
    project = get_object_or_404(Project, pk=pk)
    member = get_object_or_404(ProjectMember, pk=member_id)
    messages.success(request, "Member removed successfully.")
    member.delete()
    return redirect("projects:detail", pk=project.pk)
