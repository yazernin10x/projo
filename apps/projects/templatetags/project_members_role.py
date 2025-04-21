from django import template

from apps.projects.models import ProjectMember

register = template.Library()


@register.filter
def get_role_display(role):
    return ProjectMember.Role(role).label


@register.filter
def role_color(role):
    colors = {
        "moderator": "warning",
        "guest": "info",
        "member": "secondary",
    }
    return colors.get(role, "secondary")
