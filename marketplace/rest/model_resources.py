import json

from django.http import HttpRequest, JsonResponse
from django.views.decorators.http import require_http_methods

from marketplace.service import handle_top_ads, handle_search_ads, handle_view_ad, handle_save_update_ad


def get_top_ads():
    return JsonResponse(handle_top_ads())


@require_http_methods('POST')
def search_ads(request: HttpRequest):
    return JsonResponse(handle_search_ads(json.loads(request.body)))


@require_http_methods('POST')
def view_ad(request: HttpRequest):
    return JsonResponse(handle_view_ad(json.loads(request.body)))


@require_http_methods
def save_update_ad(request: HttpRequest):
    return JsonResponse(handle_save_update_ad(json.loads(request.body), request.user))
