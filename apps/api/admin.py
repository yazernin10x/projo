from django.contrib import admin
from apps.api.models import APIKey, APILog
from django.utils.html import format_html


@admin.register(APIKey)
class APIKeyAdmin(admin.ModelAdmin):
    list_display = ("name", "key", "user", "created_at", "is_active")
    list_filter = ("is_active", "created_at")
    search_fields = ("name", "user__username")
    readonly_fields = ("created_at", "last_used_at", "key")
    fieldsets = (
        (None, {"fields": ("key", "name", "user", "is_active")}),
        (
            "Informations temporelles",
            {"fields": ("created_at", "last_used_at"), "classes": ("collapse",)},
        ),
    )


@admin.register(APILog)
class APILogAdmin(admin.ModelAdmin):
    list_display = (
        "timestamp",
        "endpoint",
        "method",
        "status",
        "auth_type",
        "get_auth_user",
        "response_status",
    )

    list_filter = (
        "method",
        "status",
        "auth_type",
        "timestamp",
    )

    search_fields = (
        "endpoint",
        "api_key__name",
        "jwt_user__email",
        "jwt_user__username",
    )

    readonly_fields = (
        "timestamp",
        "endpoint",
        "method",
        "status",
        "auth_type",
        "api_key",
        "jwt_user",
        "request_data",
        "response_data",
    )

    fieldsets = (
        (
            "Informations de base",
            {
                "fields": (
                    "timestamp",
                    "endpoint",
                    "method",
                    "status",
                )
            },
        ),
        (
            "Authentification",
            {
                "fields": (
                    "auth_type",
                    "api_key",
                    "jwt_user",
                )
            },
        ),
        (
            "Données",
            {
                "fields": (
                    "request_data",
                    "response_data",
                ),
                "classes": ("collapse",),
            },
        ),
    )

    def get_auth_user(self, obj):
        if obj.auth_type == APILog.AuthType.API_KEY and obj.api_key:
            return f"{obj.api_key.name} (API Key)"
        elif obj.auth_type == APILog.AuthType.JWT and obj.jwt_user:
            return f"{obj.jwt_user.username} (JWT)"
        return "No authenticated"

    get_auth_user.short_description = "Utilisateur"

    def response_status(self, obj):
        status_colors = {
            "200": "green",
            "201": "green",
            "400": "orange",
            "401": "red",
            "403": "red",
            "404": "orange",
            "500": "darkred",
        }
        color = status_colors.get(str(obj.status), "black")
        return format_html(
            '<span style="color: {};">{}</span>', color, obj.get_status_display()
        )

    response_status.short_description = "Statut"

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    # def has_delete_permission(self, request, obj=None):
    #     return False
