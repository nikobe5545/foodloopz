from django.conf.urls import url

from marketplace.rest import cloudinary_resources
from marketplace.websocket import consumers

websocket_urlpatterns = [
    url(r'^marketplace/api/ws/main$', consumers.MainConsumer),
]
