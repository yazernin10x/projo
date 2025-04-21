from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_GET
from apps.projects.models import Project
from apps.tasks.models import Task
from apps.comments.models import Comment
from apps.accounts.models import User


@require_GET
@login_required
def dashboard(request):
    total_projects = Project.objects.filter(author=request.user).count()
    ongoing_projects = Project.objects.filter(
        status="ongoing", author=request.user
    ).count()
    completed_projects = Project.objects.filter(
        status="completed", author=request.user
    ).count()
    pending_projects = Project.objects.filter(
        status="pending", author=request.user
    ).count()
    cancelled_projects = Project.objects.filter(
        status="cancelled", author=request.user
    ).count()

    # Projets où l'utilisateur est membre
    member_projects = Project.objects.filter(members=request.user).count()

    tasks_todo = Task.objects.filter(status="todo", author=request.user).count()
    tasks_in_progress = Task.objects.filter(
        status="in_progress", author=request.user
    ).count()
    tasks_completed = Task.objects.filter(
        status="completed", author=request.user
    ).count()

    # Tâches assignées à l'utilisateur
    assigned_tasks = Task.objects.filter(assigned_to=request.user).count()

    # Additional KPIs
    comments_count = Comment.objects.filter(author=request.user).count()
    total_users = User.objects.count()
    active_users = User.objects.filter(is_active=True).count()

    context = {
        "total_projects": total_projects,
        "ongoing_projects": ongoing_projects,
        "completed_projects": completed_projects,
        "pending_projects": pending_projects,
        "cancelled_projects": cancelled_projects,
        "member_projects": member_projects,
        "tasks_todo": tasks_todo,
        "tasks_in_progress": tasks_in_progress,
        "tasks_completed": tasks_completed,
        "assigned_tasks": assigned_tasks,
        "comments_count": comments_count,
        "total_users": total_users,
        "active_users": active_users,
    }
    return render(request, "dashboard/dashboard.html", context)
