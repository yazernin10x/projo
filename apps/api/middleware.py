from django.utils import timezone

from .models import APILog, APIKey
from rest_framework_simplejwt.authentication import JWTAuthentication
from asgiref.sync import sync_to_async
import asyncio


class APILogMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.is_async = asyncio.iscoroutinefunction(get_response)

    async def __call__(self, request):
        if self.is_async:
            response = await self.get_response(request)
            await self.create_log(request, response)
        else:
            response = await sync_to_async(self.get_response)(request)
            await self.create_log(request, response)
        return response

    def sync_call(self, request):
        response = self.get_response(request)
        self.create_log_sync(request, response)
        return response

    def __call__(self, request):
        if asyncio.iscoroutinefunction(self.get_response):
            return self.__call__(request)
        return self.sync_call(request)

    @sync_to_async
    def create_log(self, request, response):
        self.create_log_sync(request, response)

    def create_log_sync(self, request, response):
        # Ignorer les requêtes admin, static et autres
        if not request.path.startswith("/api/"):
            return

        auth_type = APILog.AuthType.NONE
        api_key = None
        jwt_user = None

        # Vérifier l'API Key dans les headers
        api_key_header = request.headers.get("X-API-Key")
        if api_key_header:
            try:
                api_key = APIKey.objects.get(key=api_key_header, is_active=True)
                auth_type = APILog.AuthType.API_KEY
                # Mettre à jour last_used_at
                api_key.last_used_at = timezone.now()
                api_key.save()
            except APIKey.DoesNotExist:
                pass

        # Vérifier le JWT Bearer token
        elif "Authorization" in request.headers:
            auth_header = request.headers.get("Authorization", "")
            if auth_header.startswith("Bearer "):
                try:
                    jwt_auth = JWTAuthentication()
                    jwt_user, validated_token = jwt_auth.authenticate(request)
                    if jwt_user:
                        auth_type = APILog.AuthType.JWT
                except Exception:
                    pass

        # Créer le log
        APILog.objects.create(
            endpoint=request.path,
            method=request.method,
            status=response.status_code,
            auth_type=auth_type,
            api_key=api_key,
            jwt_user=jwt_user,
            request_data=self._get_request_data(request),
            response_data=self._get_response_data(response),
        )

    def _get_request_data(self, request):
        """Extraire les données de la requête"""
        data = {}

        if request.method in ["POST", "PUT", "PATCH"]:
            if hasattr(request, "data"):
                data = request.data
            else:
                try:
                    data = request.body.decode()
                except Exception:
                    pass

        elif request.method == "GET":
            data = dict(request.GET)

        return data

    def _get_response_data(self, response):
        """Extraire les données de la réponse"""
        try:
            if hasattr(response, "data"):
                return response.data
        except Exception:
            pass
        return None
