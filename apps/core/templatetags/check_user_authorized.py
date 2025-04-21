from django import template
from apps.projects.models import Project
from apps.tasks.models import Task
from apps.comments.models import Comment
from apps.projects.models import ProjectMember

register = template.Library()


@register.filter
def user_authorized(user, action):
    if isinstance(action, Project):
        return (
            user.is_superuser
            or user == action.author
            or ProjectMember.get_user_role(user, action) == "moderator"
        )
    elif isinstance(action, Task):
        return (
            user.is_superuser
            or action.author == user
            or ProjectMember.get_user_role(user, action.project) == "moderator"
        )
    elif isinstance(action, Comment):
        return (
            user.is_superuser
            or action.author == user
            or ProjectMember.get_user_role(user, action.task.project) == "moderator"
        )

    return False
