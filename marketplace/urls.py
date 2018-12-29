from django.conf.urls import url

from marketplace.rest import cloudinary

urlpatterns = [
    url(r'^api/rest/cloudinary/get-signature', cloudinary.get_signature)
]