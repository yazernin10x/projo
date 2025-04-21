from django.contrib import admin

from .models import Comment


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ["content", "task", "author", "created_at", "updated_at"]
    list_filter = ["created_at", "updated_at", "author", "task"]
    search_fields = ["content", "author__username", "task__title"]
    readonly_fields = ["created_at", "updated_at"]
    ordering = ["-created_at"]
    date_hierarchy = "created_at"

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("author", "task")
