from django.conf.urls import url
from rest_framework import routers

from marketplace.rest import cloudinary_resources
from marketplace.rest.views import AdViewSet, AdCategoryViewSet, UserProfileChangeAPIView, OrganizationChangeAPIView

router = routers.SimpleRouter()
router.register(r'api/rest/ads', AdViewSet)
router.register(r'api/rest/ad-categories', AdCategoryViewSet)
router.register(r'api/rest/users', UserProfileChangeAPIView)
router.register(r'api/rest/organizations', OrganizationChangeAPIView)

urlpatterns = [
    url(r'^api/rest/cloudinary/get-signature', cloudinary_resources.get_signature),
]

urlpatterns += router.urls
