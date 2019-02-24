from django.conf.urls import url
from rest_framework import routers
from rest_framework.documentation import include_docs_urls

from marketplace.rest import auth_resources
from marketplace.rest import cloudinary_resources
from marketplace.rest.views import AdViewSet, AdCategoryViewSet, UserProfileChangeAPIView, OrganizationChangeAPIView, \
    AdCertificationViewSet, post_new_account, confirm_email

router = routers.SimpleRouter()
router.register(r'api/rest/loops', AdViewSet)
router.register(r'api/rest/loop-categories', AdCategoryViewSet)
router.register(r'api/rest/loop-certifications', AdCertificationViewSet)
router.register(r'api/rest/users', UserProfileChangeAPIView)
router.register(r'api/rest/organizations', OrganizationChangeAPIView)

urlpatterns = [
    url(r'^api/rest/cloudinary/get-signature', cloudinary_resources.get_signature),
    url(r'^api/rest/auth/login', auth_resources.login),
    url(r'^api/rest/auth/check', auth_resources.check_login),
    url(r'^api/rest/account/register', post_new_account),
    url(r'^api/rest/account/confirm-email/(?P<uid>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        confirm_email, name='activate'),
    url(r'^api/docs', include_docs_urls(title='Foodloopz API')),
]

urlpatterns += router.urls
