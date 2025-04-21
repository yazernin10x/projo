from django.contrib import admin
from .models import Task


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ["title", "status", "project", "author", "deadline", "created_at"]
    list_filter = ["status", "project", "author", "created_at"]
    search_fields = ["title", "description", "project__title", "author__username"]
    readonly_fields = ["created_at", "updated_at"]
    filter_horizontal = ["assigned_to"]
    date_hierarchy = "created_at"
    ordering = ["-created_at"]

    fieldsets = [
        (None, {"fields": ["title", "description", "status"]}),
        ("Relations", {"fields": ["project", "author", "assigned_to"]}),
        ("Dates", {"fields": ["deadline", "created_at", "updated_at"]}),
    ]
