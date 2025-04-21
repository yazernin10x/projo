from django.db import models
from django.db.models import F, Q
from apps.accounts.models import User


class Project(models.Model):
    class Meta:
        ordering = ["title", "created_at"]
        verbose_name = "Projet"
        verbose_name_plural = "Projets"

    class Status(models.TextChoices):
        IN_PROGRESS = "in_progress", "En cours"
        COMPLETED = "completed", "Terminé"
        PENDING = "pending", "En attente"
        CANCELLED = "cancelled", "Annulé"

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
    status: models.CharField = models.CharField(
        max_length=20, choices=Status.choices, default=Status.PENDING
    )

    def __str__(self):
        return f"{self.title} - {self.author.username}"

    def __repr__(self) -> str:
        return (
            f"Project(id={self.pk}, title={self.title}, author={self.author.username})"
        )

    def get_members_with_data(self):
        return User.objects.filter(projects=self).annotate(
            role=F("project_members__role"),
            joined_at=F("project_members__joined_at"),
        )


class ProjectMember(models.Model):
    class Meta:
        # unique_together = ("user", "project")
        verbose_name = "Membre du projet"
        verbose_name_plural = "Membres du projet"
        constraints = [
            models.UniqueConstraint(
                fields=["user", "project"],
                name="unique_project_member",
                violation_error_message="Cet utilisateur fait déjà partie de ce projet.",
            )
        ]

    class Role(models.TextChoices):
        MEMBER = "member", "Membre"
        MODERATOR = "moderator", "Modérateur"
        GUEST = "guest", "Invité"

    user: models.ForeignKey = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="project_members",
        verbose_name="Utilisateur",
    )
    project: models.ForeignKey = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name="project_members",
        verbose_name="Projet",
    )
    role: models.CharField = models.CharField(
        max_length=20, choices=Role.choices, default=Role.MEMBER
    )
    joined_at: models.DateTimeField = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.project.title} ({self.role})"

    def __repr__(self) -> str:
        return f"ProjectMember(id={self.id}, user={self.user.username!r}, project={self.project.title!r}, role={self.role!r})"

    @classmethod
    def get_user_role(cls, user, project):
        project_member = cls.objects.filter(user=user, project=project).first()
        return project_member.role if project_member else None
