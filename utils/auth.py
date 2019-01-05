import datetime
import logging

import jwt
from django.contrib.auth.models import User

from foodloopz import settings
from marketplace import constant

logger = logging.getLogger(__name__)

timedelta_token_expiry = datetime.timedelta(seconds=settings.JWT_AUTH_TOKEN_EXPIRY_TIME_SECONDS)
timedelta_renewal_limit = datetime.timedelta(seconds=settings.JWT_AUTH_TOKEN_RENEWAL_LIMIT_TIME_SECONDS)


def extract_email(token):
    if not token:
        return None
    decoded_token = jwt.decode(token, settings.JWT_AUTH_SECRET_KEY,
                               algorithms=[settings.JWT_AUTH_TOKEN_ENCRYPTION_ALGORITHM],
                               options={'verify_exp': False})
    expiration_timestamp = decoded_token['exp']
    expiration_time = datetime.datetime.fromtimestamp(expiration_timestamp)
    now = datetime.datetime.utcnow()
    seven_days_ago = now - timedelta_renewal_limit
    if expiration_time > seven_days_ago:
        return decoded_token[constant.AUTH_EMAIL_KEY]
    else:
        return None


# If token is newer than 15 minutes old then we don't have to do anything
# Renew token if expiration is anywhere between 15 minutes old to 7 days old.
# When renewing we need to check if the user is still enabled (hit db)
def renew_token(email):
    now = datetime.datetime.utcnow()
    return jwt.encode({
        'exp': now + timedelta_token_expiry,
        'email': email,
        'iss': 'foodloopz'
    }, settings.JWT_AUTH_SECRET_KEY, algorithm=settings.JWT_AUTH_TOKEN_ENCRYPTION_ALGORITHM).decode('utf-8')
