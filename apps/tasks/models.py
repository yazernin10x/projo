from django.db import models
from apps.projects.models import Project
from apps.accounts.models import User


class Task(models.Model):
    class Meta:
        ordering = ["created_at"]
        verbose_name = "Task"
        verbose_name_plural = "Tasks"

    class Status(models.TextChoices):
        TODO = "todo", "À faire"
        IN_PROGRESS = "in_progress", "En cours"
        DONE = "done", "Terminée"
        CANCELLED = "cancelled", "Annulée"

    title: models.CharField = models.CharField(
        max_length=255, unique=True, null=False, blank=False
    )
    description: models.TextField = models.TextField(blank=True, null=True)
    created_at: models.DateTimeField = models.DateTimeField(auto_now_add=True)
    updated_at: models.DateTimeField = models.DateTimeField(auto_now=True)
    deadline: models.DateTimeField = models.DateTimeField(blank=True, null=True)
    status: models.CharField = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.TODO,
    )
    project: models.ForeignKey = models.ForeignKey(
        Project, on_delete=models.CASCADE, related_name="tasks"
    )
    author: models.ForeignKey = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="created_tasks"
    )
    assigned_to: models.ManyToManyField = models.ManyToManyField(
        User, related_name="assigned_tasks", blank=True
    )

    def __str__(self):
        return f"{self.title} ({self.status})"

    def __repr__(self):
        return f"Task(id={self.id}, title={self.title!r})"
