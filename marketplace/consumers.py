import json
import logging

from channels.generic.websocket import AsyncWebsocketConsumer
from django.core.serializers import serialize

from marketplace.models import Ad


class MainConsumer(AsyncWebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.logger = logging.getLogger(__name__)

    async def connect(self):
        # await self.channel_layer.group_add(
        #    self.room_group_name,
        #    self.channel_name
        # )
        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.send(text_data=json.dumps({
            'message': 'You\'re out'
        }))

    # Receive message from WebSocket
    async def receive(self, text_data=None, bytes_data=None):
        self.logger.debug(f'text_data = {text_data}, session = {self.scope["session"]}, user = {self.scope["user"]}')
        text_data_json = json.loads(text_data)
        action = text_data_json['action']
        if action == 'PUSH_ADS':
            payload = json.dumps(
                {
                    'action': 'PUSH_ADS',
                    'payload': serialize('json', Ad.objects.all())
                })
            await self.send(text_data=payload)
        # user = self.scope['user']
        # if not user.is_authenticated and not message.startswith('/login '):
        #     await self.send(text_data=json.dumps({
        #         'message': 'You must login. Write /login user pass'
        #     }))
        #     return
