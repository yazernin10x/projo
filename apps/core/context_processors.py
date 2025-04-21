from apps.notifications.models import Notification


def unread_notifications_count(request):
    if hasattr(request, "user") and request.user.is_authenticated:
        count = Notification.objects.filter(
            recipients=request.user, is_read=False
        ).count()
    else:
        count = 0
    return {"unread_notifications_count": count}
