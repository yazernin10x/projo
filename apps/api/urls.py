from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    UserViewSet,
    ProjectViewSet,
    ProjectMemberViewSet,
    TaskViewSet,
    NotificationViewSet,
    CommentViewSet,
    APIKeyViewSet,
    CustomTokenObtainPairView,
    APILogViewSet,
)

from django.urls import path, include
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework_simplejwt.views import TokenRefreshView, TokenVerifyView

router = DefaultRouter()
router.register(r"keys", APIKeyViewSet, basename="api-keys")
router.register(r"logs", APILogViewSet, basename="api-logs")
router.register(r"users", UserViewSet, basename="users")
router.register(r"projects", ProjectViewSet, basename="projects")
router.register(r"project-members", ProjectMemberViewSet, basename="project-members")
router.register(r"tasks", TaskViewSet, basename="tasks")
router.register(r"notifications", NotificationViewSet, basename="notifications")
router.register(r"comments", CommentViewSet, basename="comments")

schema_view = get_schema_view(
    openapi.Info(
        title="ProJo API",
        default_version="v1",
        description="""
        API de gestion de projets permettant de :
        * Gérer les projets et leurs membres
        * Gérer les tâches et leur attribution
        * Gérer les commentaires
        * Gérer les notifications
        """,
        terms_of_service="#",
        contact=openapi.Contact(email="contact@projo.com"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
)

app_name = "api"

urlpatterns = [
    path("", include(router.urls)),
    # Documentation URLs
    path(
        "swagger/",
        schema_view.with_ui("swagger", cache_timeout=0),
        name="schema-swagger-ui",
    ),
    path("redoc/", schema_view.with_ui("redoc", cache_timeout=0), name="schema-redoc"),
    path("openapi.json", schema_view.without_ui(cache_timeout=0), name="schema-json"),
    # URLs d'authentification
    path("auth/token/", CustomTokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("auth/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("auth/token/verify/", TokenVerifyView.as_view(), name="token_verify"),
]
