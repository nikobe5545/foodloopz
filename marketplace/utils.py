import datetime
import logging
from functools import wraps

import jwt
from django.contrib.auth.models import User

from foodloopz import settings
from marketplace import constant

logger = logging.getLogger(__name__)

timedelta_15_minutes = datetime.timedelta(minutes=15)
timedelta_7_days = datetime.timedelta(days=7)


# auth = {
#   'token': token,
#   'email': email,
#   'password': password, (only on incoming auth request)
#   'isAnonymous': True/False,
#   'expires': timestamp
# }

def websocket_jwt_auth(function):
    @wraps(function)
    def wrapper(*args, **keyword_args):
        try:
            text_data_dict = keyword_args['text_data_dict']
            auth = text_data_dict.get(constant.AUTH_KEY, {})
            token = auth.get(constant.AUTH_TOKEN_KEY, None)
            if token is not None:
                auth = _handle_jwt(auth)
            else:
                auth = create_anonymous_auth()
            payload = function(*args, **keyword_args)
            # If auth key already exists don't mess with it. Downstream function has apparently handled auth.
            if constant.AUTH_KEY in payload:
                return payload
        except Exception as e:  # NOQA
            logger.warning(f'Auth logic failed. Error = {e}')
            auth = create_anonymous_auth()
        payload[constant.AUTH_KEY] = auth
        return payload

    return wrapper


def _handle_jwt(auth):
    token = auth.get(constant.AUTH_TOKEN_KEY, None)
    decoded_token = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM],
                               options={'verify_exp': False})
    expiration_timestamp = decoded_token['exp']
    expiration_time = datetime.datetime.fromtimestamp(expiration_timestamp)
    now = datetime.datetime.utcnow()
    fifteen_minutes_ago = now - timedelta_15_minutes
    seven_days_ago = now - timedelta_7_days
    if fifteen_minutes_ago > expiration_time > seven_days_ago:
        return renew_token(decoded_token[constant.AUTH_EMAIL_KEY])
    elif expiration_time < seven_days_ago:
        return create_anonymous_auth()
    else:
        return auth


# If token is newer than 15 minutes old then we don't have to do anything
# Renew token if expiration is anywhere between 15 minutes old to 7 days old.
# When renewing we need to check if the user is still enabled (hit db)
def renew_token(email):
    auth = {}
    user = User.objects.first(email=email)
    if user.is_active:
        now = datetime.datetime.utcnow()
        auth[constant.AUTH_TOKEN_KEY] = jwt.encode({
            'exp': now + timedelta_15_minutes,
            'email': user.email,
            'iss': 'foodloopz'
        }, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)
        auth[constant.AUTH_EMAIL_KEY] = user.email
        auth[constant.AUTH_IS_ANONYMOUS_KEY] = False,
        auth[constant.AUTH_EXPIRES_KEY] = int((now + timedelta_7_days).timestamp())
    else:
        auth = create_anonymous_auth()
    return auth


def create_anonymous_auth():
    auth = {
        constant.AUTH_IS_ANONYMOUS_KEY: True
    }
    return auth
