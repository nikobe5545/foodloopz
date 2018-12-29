import json
import logging

from channels.generic.websocket import AsyncWebsocketConsumer

from marketplace.websocket import service


class MainConsumer(AsyncWebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.logger = logging.getLogger(__name__)

    async def connect(self):
        await self.accept()

    # Receive message from WebSocket
    async def receive(self, text_data=None, bytes_data=None):
        self.logger.debug(f'text_data = {text_data}, session = {self.scope["session"]}, user = {self.scope["user"]}')
        payload = service.handle_incoming_message(text_data=text_data, scope=self.scope)
        await self.send(text_data=json.dumps(payload))
