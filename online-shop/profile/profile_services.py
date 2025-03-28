from typing import Union

from django.contrib.auth.models import User
from django.core.files.storage import default_storage as storage
from django.shortcuts import get_object_or_404
from rest_framework.request import Request

from mysite.settings import AVATAR_MAX_SIZE
from profile.models import Avatar, Profile


def validate_image_func(request: Request) -> Union[str, bool]:

    """ Функция проверяет валидирует входящий файл, загружаемый для обновления аватара пользователя """

    avatar = request.FILES["avatar"]

    if avatar.size > AVATAR_MAX_SIZE:
        return 'Avatar file too large.'

    if not avatar.content_type.startswith("image/"):
        return 'Avatar file type not supported.'
    return True


def get_profile_or_404(user: User) -> Profile:

    """ Функция получения профиля пользователя, связанного через User """

    return get_object_or_404(Profile, user=user)


def update_avatar(profile, request) -> None:

    """ Функция обновляет аватар пользователя. Удаляет старый из медиа и обновляет SRC в БД """

    avatar = request.FILES['avatar']

    if profile.avatar:
        if storage.exists(profile.avatar.src.name):
            storage.delete(profile.avatar.src.name)

        profile.avatar.src = avatar
        profile.avatar.save()
    else:
        avatar_obj = Avatar.objects.create(user_profile=profile, src=avatar)
        profile.avatar = avatar_obj
        profile.save()