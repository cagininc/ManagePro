 # notifications/utils.py
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from channels.generic.websocket import AsyncWebsocketConsumer
import json


def send_notification(user_id, message):
    channel_layer = get_channel_layer()
    group_name = f'user_{user_id}'
    async_to_sync(channel_layer.group_send)(
        group_name,
        {
            'type': 'send_notification',
            'message': message
        }
    )

# Consumer tarafında çağrılacak metod
class NotificationConsumer(AsyncWebsocketConsumer):
    async def send_notification(self, event):
        message = event['message']
        await self.send(text_data=json.dumps({'message': message}))
