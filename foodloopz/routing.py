from channels.routing import ProtocolTypeRouter, URLRouter
from channels.sessions import CookieMiddleware

import marketplace.routing
from foodloopz.auth import JWTAuthMiddleware

application = ProtocolTypeRouter({
    # (http->django views is added by default)
    'websocket': CookieMiddleware(
        JWTAuthMiddleware(
            URLRouter(
                marketplace.routing.websocket_urlpatterns
            )
        )
    ),
})
