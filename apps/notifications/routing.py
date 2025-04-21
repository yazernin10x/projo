from apps.notifications import consumers
from django.urls import path

websocket_urlpatterns = [
    path(
        "ws/notifications",
        consumers.NotificationConsumer.as_asgi(),
        name="notifications_ws",
    ),
]
