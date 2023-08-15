# encoding: utf-8
from django.contrib.auth import get_user_model, authenticate
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from rest_framework import serializers
from django.utils.translation import gettext_lazy as _
from api.models import UserRequestHistory

class UserSerializer(serializers.ModelSerializer):
    """Serializer for the user object."""

    class Meta:
        model = get_user_model()
        fields = ('email', 'password', 'name')
        extra_kwargs = {'password': {'write_only': True, 'min_length': 5}}

    def create(self, validated_data):
        """Create and return a user with encrypted password."""
        return get_user_model().objects.create_user(**validated_data)
    
    def update(self, instance, validated_data):
        """Update and return user."""
        password = validated_data.pop('password', None)
        user = super().update(instance, validated_data)

        if password:
            user.set_password(password)
            user.save()

        return user

class AuthTokenSerializer(TokenObtainPairSerializer):
    """Serializer for the user auth token."""

    def validate(self, attrs):
        """Validate and authenticate the user."""
        data = super().validate(attrs)

        email = attrs.get('email')
        password = attrs.get('password')

        user = authenticate(
            username=email,
            password=password,
        )

        if not user:
            msg = _('Unable to authenticate with provided credentials.')
            raise serializers.ValidationError(msg, code='authorization')
        
        # Add extra responses here
        data.update({'email': email})

        return data
        


class UserRequestHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = UserRequestHistory
        exclude = ['id', 'user']

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        return {key: float(value) if key in ['open', 'high', 'low', 'close'] else value for key, value in representation.items() if value is not None}
        
class UserRequestStockSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserRequestHistory
        exclude = ['id', 'user','date']

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        return {key: float(value) if key in ['open', 'high', 'low', 'close'] else value for key, value in representation.items() if value is not None}