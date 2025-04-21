from django.contrib import admin
from .models import Notification


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ("content", "sender", "created_at", "is_read")
    list_filter = ("is_read", "created_at", "sender")
    search_fields = ("content", "sender__username")
    readonly_fields = ("created_at",)
    filter_horizontal = ("recipients",)
    ordering = ("-created_at",)
    date_hierarchy = "created_at"
