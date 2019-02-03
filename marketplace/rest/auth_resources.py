import json

from django.http import HttpRequest, JsonResponse, HttpResponse
from django.views.decorators.http import require_http_methods

from marketplace.auth.service import handle_login


@require_http_methods('POST')
def login(request: HttpRequest) -> HttpResponse:
    return handle_login(json.loads(request.body), request)


def check_login(request: HttpRequest) -> HttpResponse:
    return check_login(request)
