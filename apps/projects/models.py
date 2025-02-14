from django.db import models
from apps.accounts.models import User


class Project(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deadline = models.DateTimeField()
    created_by = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="created_projects"
    )
    members = models.ManyToManyField(
        User, through="ProjectMember", related_name="projects"
    )

    def __str__(self):
        return self.title


class ProjectMember(models.Model):
    ROLE_CHOICES = [
        ("admin", "Admin"),
        ("member", "Member"),
        ("guest", "Guest"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default="member")
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "project")

    def __str__(self):
        return f"{self.user.username} - {self.project.title} ({self.role})"
