from datetime import datetime

from cloudinary.utils import api_sign_request
from django.http import HttpResponse, HttpRequest
from django.views.decorators.http import require_http_methods

from foodloopz import settings


@require_http_methods('GET')
def get_signature(request: HttpRequest):
    if request.user.is_authenticated:
        parameters = request.GET.dict()
        signature = api_sign_request(parameters, settings.CLOUDINARY_SECRET_KEY)
        return HttpResponse(signature)
    else:
        return HttpResponse('Signature can\'t be created')
