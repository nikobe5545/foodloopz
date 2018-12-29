import json

from django.http import HttpRequest, JsonResponse
from django.views.decorators.http import require_http_methods

from marketplace.service import handle_change_password, handle_reset_password, handle_login, handle_save_update_user


@require_http_methods('POST')
def login(request: HttpRequest):
    return JsonResponse(handle_login(json.loads(request.body), request))


@require_http_methods('POST')
def save_update_user(request: HttpRequest):
    return JsonResponse(handle_save_update_user(json.loads(request.body), request.user))


@require_http_methods('POST')
def password_change(request: HttpRequest):
    response = handle_change_password(json.loads(request.body), request)
    return JsonResponse(response)


@require_http_methods('POST')
def password_reset(request: HttpRequest):
    response = handle_reset_password(json.loads(request.body), request)
    return JsonResponse(response)
