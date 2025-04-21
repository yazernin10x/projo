from django import template

register = template.Library()


@register.filter
def tasks_status_color(status):
    status_classes = {
        "todo": "badge-warning",
        "in_progress": "badge-info",
        "done": "badge-success",
    }
    return status_classes.get(status, "badge-neutral")


@register.filter
def filter_todo(tasks):
    return [task for task in tasks if "todo" in task.status]


@register.filter
def filter_in_progress(tasks):
    return [task for task in tasks if "in_progress" in task.status]


@register.filter
def filter_completed(tasks):
    return [task for task in tasks if "done" in task.status]
