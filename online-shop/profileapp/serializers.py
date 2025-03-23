from django.contrib.auth.models import User
from rest_framework import serializers

from profileapp.models import Avatar, Profile


class AvatarSerializer(serializers.ModelSerializer):
    class Meta:
        model = Avatar
        fields = (
            "src",
            "alt",
        )


class ProfileSerializer(serializers.ModelSerializer):

    avatar = AvatarSerializer(many=False, required=False, read_only=True)

    class Meta:
        model = Profile
        fields = (
            "fullName",
            "email",
            "phone",
            "avatar",
        )

    email = serializers.EmailField(required=False)
    phone = serializers.CharField(required=False)


class PasswordSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            "currentPassword",
            "newPassword",
        )

    currentPassword = serializers.CharField(required=True)
    newPassword = serializers.CharField(required=True)
