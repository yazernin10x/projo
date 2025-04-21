import uuid
from django.db import models
from apps.accounts.models import User
from django.utils.translation import gettext_lazy as _


class APIKey(models.Model):
    class Meta:
        verbose_name = "API Key"
        verbose_name_plural = "API Keys"

    key: models.UUIDField = models.UUIDField(
        default=uuid.uuid4, editable=False, unique=True
    )
    name: models.CharField = models.CharField(max_length=50, unique=True)
    user: models.ForeignKey = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="api_keys"
    )
    created_at: models.DateTimeField = models.DateTimeField(auto_now_add=True)
    is_active: models.BooleanField = models.BooleanField(default=True)
    last_used_at: models.DateTimeField = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.name} ({self.user.username})"


class APILog(models.Model):
    class HTTPMethod(models.TextChoices):
        GET = "GET", "GET"
        POST = "POST", "POST"
        PUT = "PUT", "PUT"
        DELETE = "DELETE", "DELETE"
        PATCH = "PATCH", "PATCH"

    class HTTPStatus(models.TextChoices):
        SUCCESS = "200", "Success"
        CREATED = "201", "Created"
        BAD_REQUEST = "400", "Bad Request"
        UNAUTHORIZED = "401", "Unauthorized"
        FORBIDDEN = "403", "Forbidden"
        NOT_FOUND = "404", "Not Found"
        SERVER_ERROR = "500", "Server Error"

    class AuthType(models.TextChoices):
        API_KEY = "API_KEY", _("API Key")
        JWT = "JWT", _("Bearer JWT")
        NONE = "NONE", _("No Authentication")

    endpoint: models.CharField = models.CharField(
        max_length=255, verbose_name=_("Endpoint")
    )
    method: models.CharField = models.CharField(
        max_length=10,
        choices=HTTPMethod.choices,
        default=HTTPMethod.GET,
        verbose_name=_("Method"),
    )
    status: models.IntegerField = models.IntegerField(
        choices=HTTPStatus.choices,
        default=HTTPStatus.SUCCESS,
        verbose_name=_("Status"),
    )
    timestamp: models.DateTimeField = models.DateTimeField(
        auto_now_add=True, verbose_name=_("Timestamp")
    )
    auth_type: models.CharField = models.CharField(
        max_length=10,
        choices=AuthType.choices,
        default=AuthType.NONE,
        verbose_name=_("Authentication Type"),
    )
    api_key: models.ForeignKey = models.ForeignKey(
        APIKey,
        on_delete=models.CASCADE,
        verbose_name=_("API Key"),
        null=True,
        blank=True,
        related_name="api_logs",
    )
    jwt_user: models.ForeignKey = models.ForeignKey(
        "accounts.User",
        on_delete=models.CASCADE,
        verbose_name=_("JWT User"),
        null=True,
        blank=True,
        related_name="jwt_api_logs",
    )
    request_data: models.JSONField = models.JSONField(
        null=True, blank=True, verbose_name=_("Request Data")
    )
    response_data: models.JSONField = models.JSONField(
        null=True, blank=True, verbose_name=_("Response Data")
    )

    class Meta:
        verbose_name = _("API Log")
        verbose_name_plural = _("API Logs")
        ordering = ["-timestamp"]

    def __str__(self):
        return f"{self.method} {self.endpoint} - {self.status}"
