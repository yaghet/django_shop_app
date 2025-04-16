from django.contrib.auth.models import User
from rest_framework import serializers


class UserLoginSerializer(serializers.Serializer):
    class Meta:
        model = User
        fields = (
            "username",
            "password",
        )
        extra_kwargs = {"password": {"write_only": True}}


class UserRegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            "username",
            "password",
        )
        extra_kwargs = {"password": {"write_only": True}}


class LogoutSerializer(serializers.Serializer):
    pass
