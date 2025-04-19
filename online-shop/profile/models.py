from django.contrib.auth.models import User
from django.db import models


def upload_avatar_profile(instance: 'Avatar', filename: str) -> str:
    """ Функция формирует путь для загрузки изображения к профилю пользователя """
    return "profile/avatar/profile_{id}/{filename}".format(
        id=instance.user_profile.user.id,
        filename=filename,
    )


class Avatar(models.Model):
    """ Модель изображения профиля пользователя, имеет связь `OneToOne` с профилем пользователя """
    class Meta:
        verbose_name = "Avatar"
        verbose_name_plural = "Avatars"

    user_profile = models.OneToOneField(
        "Profile",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="avatar_link",
    )
    src = models.ImageField(upload_to=upload_avatar_profile)
    alt = models.CharField(max_length=12, default="avatar", verbose_name="Alt Image")


class Profile(models.Model):
    """ Модель профиля пользователя, имеет связь `OneToOne` с User, и `OneToOne` c Avatar """
    class Meta:
        verbose_name = "Profile"
        verbose_name_plural = "Profiles"

    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    fullName = models.CharField(max_length=128, null=True, blank=True)
    phone = models.CharField(max_length=12, null=True, blank=True)
    email = models.EmailField(max_length=128, null=True, blank=True)
    avatar = models.OneToOneField(
        "Avatar",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="profile_link",
    )