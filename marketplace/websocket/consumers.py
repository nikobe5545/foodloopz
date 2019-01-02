import json
import logging

from channels.generic.websocket import AsyncWebsocketConsumer

from marketplace import constant
from marketplace.service import handle_top_ads, handle_login, handle_search_ads, handle_view_ad, \
    handle_save_update_ad, \
    handle_save_update_user, handle_reset_password


class MainConsumer(AsyncWebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.logger = logging.getLogger(__name__)

    async def connect(self):
        await self.accept()

    # Receive message from WebSocket
    async def receive(self, text_data=None, bytes_data=None):
        self.logger.debug(f'text_data = {text_data}, session = {self.scope["session"]}, user = {self.scope["user"]}')
        payload = _handle_incoming_message(text_data=text_data, scope=self.scope)
        if payload is not None:
            await self.send(text_data=json.dumps(payload))
        else:
            self.logger.warning(f'Action not found. Incoming data = {text_data}')


def _handle_incoming_message(text_data: str, scope):
    text_data_dict = json.loads(text_data)
    action = text_data_dict[constant.ACTION]
    payload = text_data_dict.get(constant.PAYLOAD, None)
    user = scope[constant.SESSION_SCOPE_USER]
    if action == constant.ACTION_FETCH_TOP_ADS:
        return handle_top_ads()
    if action == constant.ACTION_LOG_IN:
        return handle_login(payload, scope)
    if action == constant.ACTION_SEARCH_ADS:
        return handle_search_ads(payload)
    if action == constant.ACTION_FETCH_AD:
        return handle_view_ad(payload)
    if action == constant.ACTION_SAVE_UPDATE_AD:
        return handle_save_update_ad(payload, user)
    if action == constant.ACTION_SAVE_UPDATE_USER:
        return handle_save_update_user(payload, user)
    if action == constant.ACTION_RESET_PASSWORD:
        return handle_reset_password(scope)
