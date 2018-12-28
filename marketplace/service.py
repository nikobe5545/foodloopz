import json
import logging

from channels.auth import login
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.core.serializers import serialize
from django.db.models import Q

from marketplace import constant
from marketplace.models import Ad, Category, Organization

logger = logging.getLogger(__name__)


class NotAuthorized(Exception):
    """ Generic exception """


def handle_incoming_message(text_data: str, scope):
    text_data_dict = json.loads(text_data)
    action = text_data_dict[constant.ACTION]
    if action == constant.ACTION_TOP_ADS:
        return _handle_top_ads()
    if action == constant.ACTION_LOG_IN:
        return _handle_log_in(text_data_dict, scope)
    if action == constant.ACTION_SEARCH_ADS:
        return _handle_search_ads(text_data_dict)
    if action == constant.ACTION_VIEW_AD:
        return _handle_view_ad(text_data_dict)
    if action == constant.ACTION_SAVE_UPDATE_AD:
        return _handle_save_update_ad(text_data_dict)
    if action == constant.ACTION_SAVE_UPDATE_USER:
        return _handle_save_update_user(text_data_dict, scope)
    if action == constant.ACTION_RESET_PASSWORD:
        return _handle_reset_password(scope)


def _handle_top_ads():
    try:
        result = Ad.objects.order_by('-created')[:5]
        return _create_message_dict(constant.ACTION_TOP_ADS, constant.STATUS_OK, 'Top ads returned',
                                    serialize('json', result))
    except Exception as error:  # NOQA
        logger.warning(f'Could not fetch top ads: {error}')
        return _create_message_dict(constant.ACTION_TOP_ADS, constant.STATUS_FAIL, f'Fetching top ads failed: {error}')


def _handle_log_in(data_dict: dict, scope):
    try:
        payload = data_dict[constant.PAYLOAD]
        username = payload[constant.USERNAME]
        password = payload[constant.PASSWORD]
        user = authenticate(username=username, password=password)
        login(scope, user)
        return _create_message_dict(constant.ACTION_LOG_IN, constant.STATUS_OK, 'User logged in')
    except Exception as error:  # NOQA
        logger.debug(f'User could not be logged in: {error}')
        return _create_message_dict(constant.ACTION_LOG_IN, constant.STATUS_FAIL, f'User not logged in: {error}')


def _handle_search_ads(text_data_dict: dict):
    try:
        payload = text_data_dict[constant.PAYLOAD]
        search_phrase = payload[constant.SEARCH_PHRASE]
        category_id = payload.get(constant.CATEGORY_ID, None)
        condition = Q(heading__icontains=search_phrase) | Q(text__icontains=search_phrase)
        if category_id is not None:
            condition &= Q(category_id=category_id)
        result = Ad.objects.filter(condition)
        _create_message_dict(constant.ACTION_SEARCH_ADS, constant.STATUS_OK, 'Top ads returned',
                             serialize('json', result))
    except Exception as error:
        logger.warning(f'Search for ads failed: {error}')
        return _create_message_dict(constant.ACTION_SEARCH_ADS, constant.STATUS_FAIL, f'Search for ads failed: {error}')


def _handle_view_ad(text_data_dict: dict):
    try:
        payload = text_data_dict[constant.PAYLOAD]
        ad_id = payload[constant.AD_ID]
        result = Ad.objects.get(id=ad_id)
        _create_message_dict(constant.ACTION_VIEW_AD, constant.STATUS_OK, 'Ad returned',
                             serialize('json', result))
    except Exception as error:
        logger.warning(f'Could not find Ad: {error}')
        return _create_message_dict(constant.ACTION_VIEW_AD, constant.STATUS_FAIL, f'Search for ad failed: {error}')


def _handle_save_update_ad(text_data_dict: dict):
    try:
        payload = text_data_dict[constant.PAYLOAD]
        heading = payload[constant.HEADING]
        text = payload[constant.TEXT]
        image = payload[constant.IMAGE]
        category_id = payload[constant.CATEGORY_ID]
        organization_id = payload[constant.ORGANIZATION_ID]
        category = Category.objects.get(id=category_id)
        organization = Organization.objects.get(id=organization_id)
        ad_id = payload.get(constant.AD_ID, None)
        try:
            ad = Ad.objects.get(id=ad_id)
            ad.heading = heading
            ad.text = text
            ad.image = image
            ad.category = category
            ad.organization = organization
        except Ad.DoesNotExist:
            logger.debug('Ad not found. Creating new.')
            ad = Ad(heading=heading, text=text, image=image, category=category, organization=organization)
        ad.save()
        persisted_ad = Ad.objects.get(id=ad.id)
        _create_message_dict(constant.ACTION_SAVE_UPDATE_AD, constant.STATUS_OK, 'Ad saved/updated',
                             serialize('json', persisted_ad))
    except Exception as error:
        logger.warning(f'Ad could not be saved/updated: {error}')
        return _create_message_dict(constant.ACTION_SAVE_UPDATE_AD, constant.STATUS_FAIL,
                                    f'Save/update ad failed: {error}')


def _handle_save_update_user(text_data_dict: dict, scope):
    try:
        payload = text_data_dict[constant.PAYLOAD]
        current_user = scope[constant.SCOPE_USER]
        user_id = payload.get(constant.USER_ID, None)
        if current_user.is_authenticated and current_user.id != user_id:
            return _create_message_dict(constant.ACTION_SAVE_UPDATE_USER, constant.STATUS_FAIL,
                                        'User could not be saved/updated')
        email = payload[constant.EMAIL]
        username = payload[constant.USERNAME]
        password = payload[constant.PASSWORD]
        try:
            user = User.objects.get(id=user_id)
            user.email = email
            user.username = username
            user.set_password(password)
        except User.DoesNotExist:
            if current_user.is_anonymous:
                user = User.objects.create_user(username, email, password)
                # TODO email activation
            else:
                return _create_message_dict(constant.ACTION_SAVE_UPDATE_USER, constant.STATUS_FAIL,
                                            'User could not be saved')
        user.save()
        persisted_user = User.objects.get(id=user.id)
        return _create_message_dict(constant.ACTION_SAVE_UPDATE_USER, constant.STATUS_OK, 'User saved/updated',
                                    serialize('json', persisted_user))
    except Exception as error:
        logger.warning(f'User could not be saved/updated: {error}')
        return _create_message_dict(constant.ACTION_SAVE_UPDATE_USER, constant.STATUS_FAIL,
                                    f'Save/update user failed: {error}')


def _handle_reset_password(scope):
    # TODO email reset link if scope user is logged in
    return _create_message_dict(constant.ACTION_RESET_PASSWORD, constant.STATUS_FAIL, 'Password could not be reset')


def _create_message_dict(action: str, status: str, status_message: str, payload=None):
    message_dict = {
        constant.ACTION: action,
        constant.STATUS: status,
        constant.STATUS_MESSAGE: status_message
    }
    if payload is not None:
        message_dict[constant.PAYLOAD] = payload
    return message_dict
