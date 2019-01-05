import logging

from channels.auth import UserLazyObject
from channels.sessions import CookieMiddleware
from django.contrib.auth import get_user_model
# email == user name. Authentication made based on email only!
from django.contrib.auth.models import User, AnonymousUser
from django.db import close_old_connections
from django.utils.functional import LazyObject

from foodloopz import settings
from marketplace import constant
from utils import auth
from utils.auth import renew_token


class JWTAuthMiddleware:
    def __init__(self, inner):
        self.inner = inner
        self.logger = logging.getLogger(__name__)

    def __call__(self, scope):
        self.logger.info(f'scope = {scope}')
        return JWTAuthMiddlewareInstance(scope, self)


class JWTAuthMiddlewareInstance:
    """
    Inner class that is instantiated once per scope.
    """

    def __init__(self, scope, middleware):
        self.middleware = middleware
        self.scope = scope

        if "cookies" not in self.scope:
            raise ValueError(
                "No cookies in scope - JWTAuthMiddleware needs to run inside of CookieMiddleware."
            )
        self.activated = True
        self.scope['token'] = LazyObject()
        if 'user' not in self.scope:
            scope['user'] = UserLazyObject()
        # Instantiate our inner application
        self.inner = self.middleware.inner(self.scope)

    async def __call__(self, receive, send):
        """
        We intercept the receive() and send() callable.

        When intercepting receive() we validate the jwt token and load the user if token
        validation was successful. If token validation was unsuccessful the anonymous user is set.

        send() is intercepted so that we can set a possibly renewed token cookie in the response.

        The downstream consumer can set the token in the scope and be sure that it's set in a secure cookie
        in case the token has changed. Usable when logging the user in for instance.
        """
        # Override receive and send
        self.real_receive = receive
        self.real_send = send
        return await self.inner(self.receive, self.send)

    async def receive(self):
        """
        Overridden receive that authenticates based on token cookie
        """
        # Resolve the token
        token = self.scope['cookies'].get(settings.JWT_AUTH_TOKEN_COOKIE_NAME)
        self.scope['token'] = token
        user_email = auth.extract_email(token)
        if user_email is None:
            self.scope[constant.SESSION_SCOPE_USER]._wrapped = AnonymousUser()
        else:
            user = User.objects.filter(email=user_email).first()
            close_old_connections()
            if user.is_active:
                self.scope[constant.SESSION_SCOPE_USER]._wrapped = user
            else:
                self.scope[constant.SESSION_SCOPE_USER]._wrapped = AnonymousUser()
        return await self.real_receive()

    async def send(self, message):
        """
        Overridden send that also sets a new token cookie if needed.
        """
        if self.activated:
            user = self.scope[constant.SESSION_SCOPE_USER]
            if user.is_authenticated:
                # Renew the token and set it in the token cookie
                token = renew_token(user.email)
                old_token = self.scope['token']
                if token != old_token:
                    CookieMiddleware.set_cookie(
                        message,
                        settings.JWT_AUTH_TOKEN_COOKIE_NAME,
                        value=token,
                        secure=True,
                        httponly=True
                    )
            else:
                CookieMiddleware.delete_cookie(message, settings.JWT_AUTH_TOKEN_COOKIE_NAME)
        # Pass up the send
        return await self.real_send(message)


# Authenticating on email instead of username
class EmailBackend:
    @staticmethod
    def authenticate(request, username=None, password=None):
        user_model = get_user_model()
        try:
            user = user_model.objects.get(email=username)
        except user_model.DoesNotExist:
            return None
        else:
            if user.check_password(password):
                return user
        return None

    @staticmethod
    def get_user(user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
