from django.conf.urls import url

from marketplace.rest import cloudinary_resources, auth_resources, model_resources

urlpatterns = [
    url(r'^api/rest/cloudinary/get-signature', cloudinary_resources.get_signature),
    url(r'^api/rest/user/login', auth_resources.handle_login),
    url(r'^api/rest/user/save-update', auth_resources.handle_save_update_user),
    url(r'^api/rest/user/reset-password', auth_resources.handle_reset_password),
    url(r'^api/rest/user/change-password', auth_resources.handle_change_password),
    url(r'^api/rest/ad/top-ads', model_resources.get_top_ads),
    url(r'^api/rest/ad/view', model_resources.view_ad),
    url(r'^api/rest/ad/save-update', model_resources.save_update_ad),
    url(r'^api/rest/ad/search', model_resources.search_ads),
]
