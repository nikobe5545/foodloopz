from django.contrib.auth.models import User
from rest_framework import serializers

from marketplace.models import Ad, Organization, Account


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'id')


class OrganizationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organization
        fields = '__all__'
        depth = 1


class AccountSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = Account
        fields = '__all__'


class AdSerializer(serializers.ModelSerializer):
    account = AccountSerializer()

    class Meta:
        model = Ad
        fields = '__all__'
        depth = 1
