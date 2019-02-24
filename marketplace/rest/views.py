import logging
from http import HTTPStatus

from django.contrib.auth import get_user_model, login
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from rest_framework import permissions, viewsets
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.request import Request
from rest_framework.response import Response

from marketplace import constant
from marketplace.models import Account, Organization, Ad, AdCategory, AdCertification
from marketplace.rest.permissions import IsNotAuthenticated
from marketplace.rest.serializers import AdSerializer, AdCategorySerializer, OrganizationSerializer, UserSerializer, \
    AdCertificationSerializer
from marketplace.rest.validation import validate_new_user, validate_new_organization, UserAlreadyExistsException, \
    OrganizationAlreadyExistsException
from marketplace.service import get_top_ads, handle_new_user_and_organization, handle_new_user

logger = logging.getLogger(__name__)

User = get_user_model()


class IsOwnerOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.account.user.id == request.user.id


class AdViewSet(viewsets.ModelViewSet):
    queryset = Ad.objects.all()
    serializer_class = AdSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]

    @action(detail=False, methods=['get'], url_path='top-ads')
    def top_ads(self, request):
        top_ads = get_top_ads()
        serializer = AdSerializer(top_ads, many=True)
        return Response(serializer.data)


class AdCategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = AdCategory.objects.all()
    serializer_class = AdCategorySerializer
    permission_classes = [permissions.IsAuthenticated]


class AdCertificationViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = AdCertification.objects.all()
    serializer_class = AdCertificationSerializer
    permission_classes = [permissions.IsAuthenticated]


class UserIsOwnerOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.id == request.user.id


class UserProfileChangeAPIView(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [
        permissions.IsAuthenticated,
        UserIsOwnerOrReadOnly
    ]


class UserIsOrganizationOwnerOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        account = Account.objects.filter(user=request.user).first()
        return obj.id == account.organization.id
        # TODO add group or permission check here.
        # Only one user within the org should have admin rights.


class OrganizationChangeAPIView(viewsets.ModelViewSet):
    queryset = Organization.objects.all()
    serializer_class = OrganizationSerializer
    permission_classes = (
        permissions.IsAuthenticated,
        UserIsOrganizationOwnerOrReadOnly,
    )


# # Function based views below

@api_view(['POST'])
@permission_classes([IsNotAuthenticated])
def post_new_account(request: Request) -> Response:
    post_data = request.data
    try:
        user_data = post_data[constant.USER]
        validate_new_user(user_data)
        organization_data = post_data[constant.ORGANIZATION]
        validate_new_organization(organization_data)
    except UserAlreadyExistsException as e:
        return Response({'fail': e}, status=HTTPStatus.BAD_REQUEST)
    # Check if organization already exists. Fail if that is the case
    except OrganizationAlreadyExistsException:
        user, organization = handle_new_user(post_data)
        data = _create_user_organization_data(user, organization)
        return Response(data)
    user, organization = handle_new_user_and_organization(post_data)
    data = _create_user_organization_data(user, organization)
    return Response(data)


def _create_user_organization_data(user: User, organization: Organization) -> dict:
    serialized_user = UserSerializer(user).data
    serialized_organization = OrganizationSerializer(organization).data
    data = {
        constant.USER: serialized_user,
        constant.ORGANIZATION: serialized_organization
    }
    return data


@api_view(['GET'])
def confirm_email(request: Request, uid: str, token: str) -> Response:
    try:
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    generator = PasswordResetTokenGenerator()
    if user is not None and generator.check_token(user, token):
        user.is_active = True
        user.save()
        login(request, user)
        return Response({'success': True})
    else:
        return Response({'success': False})
