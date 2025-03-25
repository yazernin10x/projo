from django.db import models
from apps.accounts.models import User


class Project(models.Model):
    title: models.CharField = models.CharField(max_length=255, unique=True)
    description: models.TextField = models.TextField(blank=True, null=True)
    created_at: models.DateTimeField = models.DateTimeField(auto_now_add=True)
    updated_at: models.DateTimeField = models.DateTimeField(auto_now=True)
    deadline: models.DateTimeField = models.DateTimeField(blank=True, null=True)
    author: models.ForeignKey = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="created_projects"
    )
    members: models.ManyToManyField = models.ManyToManyField(
        User, through="ProjectMember", related_name="projects", blank=True
    )

    def __str__(self):
        return f"{self.title} - {self.author.username}"

    def __repr__(self) -> str:
        return (
            f"Project(id={self.id}, title={self.title}, author={self.author.username})"
        )


class ProjectMember(models.Model):
    class Role(models.TextChoices):
        NONE = "none", "Choisir..."
        MEMBER = "member", "Membre"
        MODERATOR = "moderator", "Modérateur"
        GUEST = "guest", "Invité"

    user: models.ForeignKey = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="project_members"
    )
    project: models.ForeignKey = models.ForeignKey(
        Project, on_delete=models.CASCADE, related_name="project_members"
    )
    role: models.CharField = models.CharField(
        max_length=20, choices=Role.choices, default=Role.MEMBER
    )
    joined_at: models.DateTimeField = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "project")

    def __str__(self):
        return f"{self.user.username} - {self.project.title} ({self.role})"

    def __repr__(self) -> str:
        return f"ProjectMember(id={self.id}, user={self.user.username}, project={self.project.title}, role={self.role})"
