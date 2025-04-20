import re
from profile.models import Avatar, Profile

from django.contrib.auth.models import User
from rest_framework import serializers


class AvatarSerializer(serializers.ModelSerializer):
    """

    Сериализатор для модели Avatar.

    Поля:
    - src: ссылка на изображение аватара.
    - alt: альтернативный текст для изображения.
    """

    class Meta:
        model = Avatar
        fields = (
            "src",
            "alt",
        )


class ProfileSerializer(serializers.ModelSerializer):
    """

    Сериализатор для модели Profile
    Содержит методы для валидации номера телефона и имени профиля пользователя
    (с использованием встроенной библиотеки `re`)

    Поля:
    - fullName: полное имя пользователя.
    - email: адрес электронной почты (необязательное).
    - phone: номер телефона (необязательное).
    - avatar: аватар пользователя (вложенный сериализатор).
    """

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

    def validate_phone(self, value):

        """ Метод для проверки валидности номера телефона """

        if not re.match(r'^\+?\d{10,15}$', value):
            raise serializers.ValidationError(
                "Неверный формат телефона. Ожидается от 10 до 15 цифр, может начинаться с +")
        return value

    def validate_fullName(self, value):

        """ Метод для проверки валидности имени профиля пользователя  """

        if not re.match(r'^[A-Za-zА-Яа-яЁё\s\-]{5,}$', value):
            raise serializers.ValidationError(
                "Полное имя должно содержать минимум 5 букв и может включать пробелы и дефисы")
        return value


class PasswordSerializer(serializers.ModelSerializer):
    """

    Сериализатор для изменения пароля пользователя.

    Поля:
    - currentPassword: текущий пароль пользователя (обязательное).
    - newPassword: новый пароль пользователя (обязательное).
    """
    class Meta:
        model = User
        fields = (
            "currentPassword",
            "newPassword",
        )

    currentPassword = serializers.CharField(required=True)
    newPassword = serializers.CharField(required=True)
