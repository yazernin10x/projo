from django import template

register = template.Library()


@register.filter
def filter_ongoing(projects):
    return [p for p in projects if p.status == "ongoing"]


@register.filter
def filter_completed(projects):
    return [p for p in projects if p.status == "completed"]


@register.filter
def filter_pending(projects):
    return [p for p in projects if p.status == "pending"]


@register.filter
def filter_cancelled(projects):
    return [p for p in projects if p.status == "cancelled"]


@register.filter
def tasks_status_color(status):
    tasks_status_colors = {
        "ongoing": "badge-info",
        "completed": "badge-success",
        "pending": "badge-warning",
        "cancelled": "badge-error",
    }
    return tasks_status_colors.get(status, "badge-info")
