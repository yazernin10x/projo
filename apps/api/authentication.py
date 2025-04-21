from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from django.utils import timezone
from apps.api.models import APIKey


class APIKeyAuthentication(BaseAuthentication):
    def authenticate(self, request):
        api_key = request.META.get("HTTP_X_API_KEY")
        if not api_key:
            return None

        try:
            api_key_obj = APIKey.objects.select_related("user").get(
                key=api_key, is_active=True
            )
            # Mettre à jour la dernière utilisation
            api_key_obj.last_used_at = timezone.now()
            api_key_obj.save(update_fields=["last_used_at"])

            return (api_key_obj.user, api_key_obj)
        except (APIKey.DoesNotExist, ValueError):
            raise AuthenticationFailed("API Key invalide")
