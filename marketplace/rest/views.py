from django.contrib.auth import get_user_model
from rest_framework import permissions, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from marketplace.models import Account, Organization, Ad, AdCategory, AdCertification
from marketplace.serializers import AdSerializer, AdCategorySerializer, OrganizationSerializer, UserSerializer, \
    AdCertificationSerializer
from marketplace.service import get_top_ads

User = get_user_model()


class IsOwnerOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.account.user.id == request.user.id


class AdViewSet(viewsets.ModelViewSet):
    queryset = Ad.objects.all()
    serializer_class = AdSerializer
    permission_classes = [IsOwnerOrReadOnly, permissions.IsAuthenticated]

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
