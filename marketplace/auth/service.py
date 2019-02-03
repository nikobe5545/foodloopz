import logging

from django.contrib.auth import login, authenticate
from django.contrib.auth.models import User
from django.http import JsonResponse, HttpRequest

from marketplace import constant
from marketplace.models import Account

logger = logging.getLogger(__name__)


def handle_login(payload: dict, request) -> JsonResponse:
    try:
        email = payload[constant.EMAIL]
        password = payload[constant.PASSWORD]
        user = authenticate(username=email, password=password)
        if user is not None:
            login(request, user)
            payload = create_auth_response_payload(user)
            return JsonResponse(payload)
    except Exception as error:
        logger.debug(f'User could not be logged in: {error}')
    payload = {
        'errorMessage': 'User could not be authenticated'
    }
    return JsonResponse(payload, status=403)


def create_auth_response_payload(user: User) -> dict:
    account = Account.objects.filter(user=user).first()
    payload = {
        'email': user.email,
        'roles': [group.name for group in user.groups.all()],
        'organization': account.organization.id
    }
    return payload


def check_login(request: HttpRequest) -> JsonResponse:
    user = request.user
    if user.is_authenticated:
        return JsonResponse(create_auth_response_payload(user))
    else:
        return JsonResponse({
            'email': None,
            'roles': [],
            'organization': None
        })
