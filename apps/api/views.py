from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.views import TokenObtainPairView
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import AnonymousUser
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from apps.tasks.models import Task
from apps.projects.models import Project, ProjectMember
from apps.notifications.models import Notification
from apps.accounts.models import User
from apps.comments.models import Comment
from .serializers import (
    UserSerializer,
    ProjectSerializer,
    ProjectMemberSerializer,
    TaskSerializer,
    NotificationSerializer,
    CommentSerializer,
    APIKeySerializer,
    CustomTokenObtainPairSerializer,
    APILogSerializer,
)
from apps.api.models import APIKey, APILog


class APIKeyViewSet(viewsets.ModelViewSet):
    """
    ViewSet pour la gestion des clés API.
    """

    serializer_class = APIKeySerializer

    def get_queryset(self):
        return APIKey.objects.filter(user=self.request.user)

    @swagger_auto_schema(
        operation_description="Générer une nouvelle clé API",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=["name"],
            properties={
                "name": openapi.Schema(
                    type=openapi.TYPE_STRING, description="Nom de la clé API"
                ),
            },
        ),
        responses={201: APIKeySerializer, 400: "Données invalides"},
    )
    @action(detail=False, methods=["post"])
    def generate(self, request):
        """Générer une nouvelle clé API pour l'utilisateur"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(user=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @swagger_auto_schema(
        operation_description="Révoquer une clé API",
        responses={204: "Clé révoquée avec succès", 404: "Clé non trouvée"},
    )
    @action(detail=True, methods=["post"])
    def revoke(self, request, pk=None):
        """Révoquer une clé API existante"""
        api_key = self.get_object()
        api_key.is_active = False
        api_key.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


class APILogViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet pour consulter les journaux d'API.
    Lecture seule - pas de création/modification/suppression via l'API
    """

    queryset = APILog.objects.all()
    serializer_class = APILogSerializer
    permission_classes = [permissions.IsAdminUser]

    def get_queryset(self):
        queryset = APILog.objects.all()
        # Filtrage par date
        # Récupère les logs à partir d'une date donnée.
        date_from = self.request.query_params.get("date_from", None)
        # Récupère les logs jusqu'à une date donnée.
        date_to = self.request.query_params.get("date_to", None)

        if date_from:
            queryset = queryset.filter(timestamp__gte=date_from)
        if date_to:
            queryset = queryset.filter(timestamp__lte=date_to)

        return queryset


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get_queryset(self):
        return User.objects.filter(is_active=True)


class ProjectViewSet(viewsets.ModelViewSet):
    """
    ViewSet pour la gestion des projets.

    Permet de créer, lire, mettre à jour et supprimer des projets.
    Seuls les membres d'un projet peuvent y accéder.
    """

    queryset = Project.objects.all()
    serializer_class = ProjectSerializer

    def get_queryset(self):
        return Project.objects.filter(author=self.request.user).select_related("author")

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @swagger_auto_schema(
        operation_description="Récupérer les projets dont l'utilisateur est membre",
        responses={
            200: ProjectSerializer(many=True),
        },
    )
    @action(detail=False, methods=["get"], url_path="my-memberships")
    def my_memberships(self, request):
        """
        Récupère tous les projets dont l'utilisateur courant est membre.
        """
        projects = Project.objects.filter(members=request.user).select_related("author")
        serializer = self.get_serializer(projects, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_description="Ajouter un membre à un projet",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=["user_id"],
            properties={
                "user_id": openapi.Schema(type=openapi.TYPE_INTEGER),
                "role": openapi.Schema(
                    type=openapi.TYPE_STRING, default="member", enum=["admin", "member"]
                ),
            },
        ),
        responses={
            200: ProjectMemberSerializer,
            404: "Utilisateur non trouvé",
            403: "Permission refusée",
        },
    )
    @action(detail=True, methods=["post"], url_path="add-member")
    def add_member(self, request, pk=None):
        """
        Ajoute un membre au projet.

        Parameters:
            - user_id: ID de l'utilisateur à ajouter
            - role: Rôle du membre (default: 'member')
        """
        project = self.get_object()
        user_id = request.data.get("user_id")
        role = request.data.get("role", "member")

        user = get_object_or_404(User, id=user_id)
        member = ProjectMember.objects.create(project=project, user=user, role=role)

        serializer = ProjectMemberSerializer(member)
        return Response(serializer.data)


class ProjectMemberViewSet(viewsets.ModelViewSet):
    queryset = ProjectMember.objects.all()
    serializer_class = ProjectMemberSerializer

    def get_queryset(self):
        return ProjectMember.objects.filter(
            project__members=self.request.user
        ).select_related("user", "project")


class TaskViewSet(viewsets.ModelViewSet):
    """
    ViewSet pour la gestion des tâches.

    Permet de créer, lire, mettre à jour et supprimer des tâches.
    Seuls les membres du projet associé peuvent accéder aux tâches.
    """

    queryset = Task.objects.all()
    serializer_class = TaskSerializer

    def get_queryset(self):
        return Task.objects.filter(project__members=self.request.user).select_related(
            "project", "author"
        )

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @swagger_auto_schema(
        operation_description="Assigner un utilisateur à une tâche",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=["user_id"],
            properties={
                "user_id": openapi.Schema(type=openapi.TYPE_INTEGER),
            },
        ),
        responses={
            200: TaskSerializer,
            404: "Utilisateur ou tâche non trouvé",
            403: "Permission refusée",
        },
    )
    @action(detail=True, methods=["post"], url_path="assign-user")
    def assign_user(self, request, pk=None):
        """
        Assigne un utilisateur à une tâche.

        Parameters:
            - user_id: ID de l'utilisateur à assigner
        """
        task = self.get_object()
        user_id = request.data.get("user_id")
        user = get_object_or_404(User, id=user_id)

        task.assigned_to.add(user)
        serializer = self.get_serializer(task)
        return Response(serializer.data)


class NotificationViewSet(viewsets.ModelViewSet):
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer

    def get_queryset(self):
        return Notification.objects.filter(recipients=self.request.user).select_related(
            "sender"
        )

    def perform_create(self, serializer):
        serializer.save(sender=self.request.user)

    @action(detail=True, methods=["post"], url_path="mark-as-read")
    def mark_as_read(self, request, pk=None):
        notification = self.get_object()
        notification.is_read = True
        notification.save()
        serializer = self.get_serializer(notification)
        return Response(serializer.data)


from rest_framework.views import APIView


class BaseAPIView(APIView):
    def initial(self, request, *args, **kwargs):
        super().initial(request, *args, **kwargs)
        if isinstance(request.user, AnonymousUser):
            # Gérer l'accès anonyme selon vos besoins
            if not self.allow_anonymous():
                return Response(
                    {"detail": "Authentication required."},
                    status=status.HTTP_401_UNAUTHORIZED,
                )

    def allow_anonymous(self):
        """
        Surcharger cette méthode dans les vues enfants pour autoriser l'accès anonyme
        """
        return False


class CommentViewSet(BaseAPIView, viewsets.ModelViewSet):
    """
    ViewSet pour la gestion des commentaires.

    Permet de créer, lire, mettre à jour et supprimer des commentaires.
    Seuls les membres du projet associé à la tâche peuvent accéder aux commentaires.
    """

    queryset = Comment.objects.all()
    serializer_class = CommentSerializer

    def get_queryset(self):
        print(self.request.user, "**********************************")
        return Comment.objects.filter(
            task__project__members=self.request.user
        ).select_related("author", "task")

    def perform_create(self, serializer):
        task = get_object_or_404(
            Task, pk=self.request.data.get("task"), project__members=self.request.user
        )
        serializer.save(author=self.request.user, task=task)

    @swagger_auto_schema(
        operation_description="Récupérer les commentaires d'une tâche",
        manual_parameters=[
            openapi.Parameter(
                "pk",
                openapi.IN_PATH,
                description="ID de la tâche",
                type=openapi.TYPE_INTEGER,
            )
        ],
        responses={
            200: CommentSerializer(many=True),
            404: "Tâche non trouvée",
            403: "Permission refusée",
        },
    )
    @action(detail=True, methods=["get"], url_path="task-comments")
    def task_comments(self, request, pk=None):
        """
        Récupère tous les commentaires d'une tâche spécifique.
        """
        task = get_object_or_404(Task, id=pk, project__members=request.user)
        comments = self.get_queryset().filter(task=task)
        serializer = self.get_serializer(comments, many=True)
        return Response(serializer.data)
