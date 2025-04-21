from django.urls import reverse_lazy
from django.contrib import messages
from django.db.models import Q
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_GET, require_POST
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.messages.views import SuccessMessageMixin
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView,
)

from apps.accounts.models import User
from apps.projects.models import Project, ProjectMember
from apps.projects.forms import ProjectForm, ProjectMemberFormSet
from apps.core.logging import get_logger
from apps.core.constants import HTTP_400_BAD_REQUEST, HTTP_403_FORBIDDEN

logger = get_logger("projects.views")


class ProjectListView(SuccessMessageMixin, LoginRequiredMixin, ListView):
    model = Project
    template_name = "projects/list.html"
    context_object_name = "projects"
    success_message = "Projet créé avec succès."
    paginate_by = 10
    paginate_orphans = 2

    def get_queryset(self):
        return Project.objects.filter(author=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Pagination des projets dont l'utilisateur est membre
        member_projects = Project.objects.filter(members=self.request.user)
        member_page = self.request.GET.get("member_page", 1)
        member_paginator = Paginator(member_projects, self.paginate_by)
        context["page_member_projects"] = member_paginator.get_page(member_page)
        return context


class ProjectDetailView(SuccessMessageMixin, LoginRequiredMixin, DetailView):
    model = Project
    template_name = "projects/detail.html"
    context_object_name = "project"
    tasks_per_page = 6
    members_per_page = 5

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        project_members = self.object.get_members_with_data()

        # Pagination des membres
        member_page = self.request.GET.get("member_page", 1)
        member_paginator = Paginator(project_members, self.members_per_page)
        context["page_project_members"] = member_paginator.get_page(member_page)

        # Application des filtres sur les tâches
        tasks = self.object.tasks.filter(
            Q(author=self.request.user) | Q(assigned_to=self.request.user)
        )
        status = self.request.GET.get("status")
        deadline = self.request.GET.get("deadline")

        if status:
            tasks = tasks.filter(status=status)
        if deadline:
            tasks = tasks.filter(deadline__exact=deadline)

        context["tasks"] = tasks
        # Pagination des tâches créées
        created_tasks = tasks.filter(author=self.request.user)
        created_page = self.request.GET.get("created_page", 1)
        created_paginator = Paginator(created_tasks, self.tasks_per_page)
        context["page_created_tasks"] = created_paginator.get_page(created_page)

        # Pagination des tâches assignées
        assigned_tasks = tasks.filter(assigned_to=self.request.user)
        assigned_page = self.request.GET.get("assigned_page", 1)
        assigned_paginator = Paginator(assigned_tasks, self.tasks_per_page)
        context["page_assigned_tasks"] = assigned_paginator.get_page(assigned_page)

        return context


class ProjectCreateView(SuccessMessageMixin, LoginRequiredMixin, CreateView):
    model = Project
    form_class = ProjectForm
    template_name = "projects/project_form.html"
    success_message = "Projet créé avec succès."

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy("projects:detail", kwargs={"pk": self.object.pk})


class ProjectUpdateView(SuccessMessageMixin, LoginRequiredMixin, UpdateView):
    model = Project
    form_class = ProjectForm
    template_name = "projects/project_form.html"
    context_object_name = "project"
    success_message = "Projet mis à jour avec succès."

    def get_success_url(self):
        return reverse_lazy("projects:detail", kwargs={"pk": self.object.pk})


class ProjectDeleteView(SuccessMessageMixin, LoginRequiredMixin, DeleteView):
    model = Project
    success_message = "Projet supprimé avec succès."
    success_url = reverse_lazy("projects:list")


@login_required
def manage_members(request, pk: int):
    project = get_object_or_404(Project, pk=pk)
    project_members_formset = ProjectMemberFormSet(
        request.POST or None,
        instance=project if project.members.exists() else None,
        prefix="project-members",
        form_kwargs={"user": request.user, "project": project},
    )

    if request.method == "POST" and project_members_formset.is_valid():
        project_members_formset.save(commit=False)

        # Traitement des formulaires
        for form in project_members_formset:
            # Vérification si le membre est nouveau
            if not form.instance.pk:
                member = form.save(commit=False)
                member.project = project
                member.save()
            # Mise à jour des membres existants
            else:
                if form.instance in project_members_formset.deleted_objects:
                    form.instance.delete()
                else:
                    if form.has_changed():
                        update_fields = form.changed_data
                        if "DELETE" in update_fields:
                            update_fields.remove("DELETE")

                        if update_fields:
                            form.instance.save(update_fields=update_fields)

        messages.success(request, "Les modifications ont été enregistrées.")
        return redirect("projects:detail", pk=project.pk)

    return render(
        request,
        "projects/project_members_form.html",
        {"project": project, "project_members_formset": project_members_formset},
    )


@require_POST
@login_required
def remove_member(request, pk: int, member_pk: int):
    project = get_object_or_404(Project, pk=pk)
    user = get_object_or_404(User, pk=member_pk)
    member = get_object_or_404(ProjectMember, project=project, user=user)
    member.delete()
    messages.success(request, "Membre retiré avec succès.")
    return redirect("projects:detail", pk=project.pk)


@require_POST
@login_required
def update_project_status(request, pk):
    project = get_object_or_404(Project, pk=pk)
    if not (
        request.user.is_superuser
        or request.user == project.author
        or ProjectMember.objects.filter(
            user=request.user, project=project, role="moderator"
        ).exists()
    ):
        return JsonResponse(
            {"status": "error", "message": "Permission refusée"},
            status=HTTP_403_FORBIDDEN,
        )

    if request.method == "POST":
        new_status = request.POST.get("status")
        if new_status in dict(Project.Status.choices):
            project.status = new_status
            project.save()
            return JsonResponse(
                {
                    "status": "success",
                    "project_status": new_status,
                    "project_status_display": project.get_status_display(),
                }
            )

    return JsonResponse(
        {"status": "error", "message": "Statut invalide"},
        status=HTTP_400_BAD_REQUEST,
    )
