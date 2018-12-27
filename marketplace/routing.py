from django.conf.urls import url

from . import consumers

websocket_urlpatterns = [
    url(r'^marketplace/api/ws/main$', consumers.MainConsumer),
]
