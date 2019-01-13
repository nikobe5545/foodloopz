from django.conf.urls import url
from rest_framework import routers

from marketplace.rest import cloudinary_resources
from marketplace.rest.views import AdViewSet, AdCategoryViewSet, UserProfileChangeAPIView, OrganizationChangeAPIView, \
    AdCertificationViewSet

router = routers.SimpleRouter()
router.register(r'api/rest/loops', AdViewSet)
router.register(r'api/rest/loop-categories', AdCategoryViewSet)
router.register(r'api/rest/loop-certifications', AdCertificationViewSet)
router.register(r'api/rest/users', UserProfileChangeAPIView)
router.register(r'api/rest/organizations', OrganizationChangeAPIView)

urlpatterns = [
    url(r'^api/rest/cloudinary/get-signature', cloudinary_resources.get_signature),
]

urlpatterns += router.urls
