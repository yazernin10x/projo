from django.contrib import admin
from apps.projects.models import Project, ProjectMember


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ("title", "author", "status", "deadline", "created_at")
    list_filter = ("status", "created_at", "deadline")
    search_fields = ("title", "description", "author__username")
    readonly_fields = ("created_at", "updated_at")
    fieldsets = (
        (None, {"fields": ("title", "description", "status", "deadline")}),
        ("Auteur", {"fields": ("author",)}),
        ("Dates", {"fields": ("created_at", "updated_at"), "classes": ("collapse",)}),
    )


@admin.register(ProjectMember)
class ProjectMemberAdmin(admin.ModelAdmin):
    list_display = ("user", "project", "role", "joined_at")
    list_filter = ("role", "joined_at")
    search_fields = ("user__username", "project__title")
    readonly_fields = ("joined_at",)
