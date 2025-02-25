from django import template

register = template.Library()


@register.filter
def role_color(role):
    colors = {
        "moderator": "warning",
        "guest": "info",
        "member": "secondary",
    }
    return colors.get(role, "secondary")
