import json
from channels.generic.websocket import AsyncWebsocketConsumer
import logging

logger = logging.getLogger(__name__)

class ManagerNotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.group_name = 'managers_notifications'
        try:
            logger.debug(f"[DEBUG] Connecting user to group: {self.group_name}")

            await self.channel_layer.group_add(
                self.group_name,
                self.channel_name
            )
            await self.accept()
            logger.debug(f"[DEBUG] Connected to group: {self.group_name}")
        except Exception as e:
            logger.error(f"[ERROR] Error during connect: {e}")

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )
        logger.debug(f"[DEBUG] Disconnected from group: {self.group_name}")

    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
            message = data['message']
            logger.debug(f"[DEBUG] Message received: {message}")

            # Bildirimi tüm grup üyelerine gönder
            await self.channel_layer.group_send(
                self.group_name,
                {
                    'type': 'notification_message',
                    'message': message
                }
            )
            logger.debug(f"[DEBUG] Message sent to group: {self.group_name}")
        except Exception as e:
            logger.error(f"[ERROR] Error during receive: {e}")

    async def notification_message(self, event):
        message = event['message']
        try:
            # WebSocket üzerinden frontend'e gönder
            logger.debug(f"[DEBUG] Sending message to frontend: {message}")
            await self.send(text_data=json.dumps({
                'message': message
            }))
        except Exception as e:
            logger.error(f"[ERROR] Error during sending to frontend: {e}")
