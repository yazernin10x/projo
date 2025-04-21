import json
from channels.generic.websocket import AsyncWebsocketConsumer

from apps.core.logging import get_logger

logger = get_logger("notifications.consumers")


class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.group_name = f"user_{self.scope['user'].pk}"
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        if data["type"] == "acknowledgment":
            logger.info(f"Notification reçue par {self.scope['user'].username}")

    async def send_notification(self, event):
        await self.send(
            text_data=json.dumps(
                {
                    "type": "notification",
                    "title": event["title"],
                    "content": event["content"],
                }
            )
        )
