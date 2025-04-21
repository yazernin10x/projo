from rest_framework import serializers

from apps.api.models import APIKey, APILog
from apps.tasks.models import Task
from apps.projects.models import Project, ProjectMember
from apps.notifications.models import Notification
from apps.accounts.models import User
from apps.comments.models import Comment

from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


class APIKeySerializer(serializers.ModelSerializer):
    key = serializers.UUIDField(read_only=True)

    class Meta:
        model = APIKey
        fields = ["id", "key", "name", "created_at", "last_used_at", "is_active"]
        read_only_fields = ["key", "created_at", "last_used_at"]


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        # Ajout d'informations supplémentaires dans la réponse
        data["username"] = self.user.username
        data["email"] = self.user.email
        return data


class APILogSerializer(serializers.ModelSerializer):
    class Meta:
        model = APILog
        fields = [
            "id",
            "endpoint",
            "method",
            "status",
            "timestamp",
            "api_key",
            "request_data",
            "response_data",
        ]
        read_only_fields = fields


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "email", "first_name", "last_name"]


class ProjectMemberSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = ProjectMember
        fields = "__all__"
        read_only_fields = ["joined_at"]


class ProjectSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)

    class Meta:
        model = Project
        fields = "__all__"
        read_only_fields = ["created_at", "updated_at"]


class TaskSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    assigned_to = UserSerializer(many=True, read_only=True)

    class Meta:
        model = Task
        fields = "__all__"
        read_only_fields = ["created_at", "updated_at"]


class NotificationSerializer(serializers.ModelSerializer):
    sender = UserSerializer(read_only=True)
    recipients = UserSerializer(many=True, read_only=True)

    class Meta:
        model = Notification
        fields = "__all__"
        read_only_fields = ["created_at", "sender", "recipients"]


class CommentSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)

    class Meta:
        model = Comment
        fields = ["id", "content", "created_at", "updated_at", "author", "task"]
        read_only_fields = ["created_at", "updated_at", "author"]
