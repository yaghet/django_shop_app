from django.contrib.auth.models import User
from django.core.validators import (EmailValidator, MaxLengthValidator,
                                    MinLengthValidator)
from django.db import models


def upload_avatar_profile(instance, filename):
    return "profiles/profile_{id}/preview/{filename}".format(
        id=instance.pk, filename=filename,
    )


class Profile(models.Model):

    class Meta:
        verbose_name = 'Profile'
        verbose_name_plural = 'Profiles'

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    middle_name = models.CharField(max_length=30)
    email = models.EmailField(validators=[EmailValidator])
    phone = models.CharField(max_length=30, validators=[MinLengthValidator(10), MaxLengthValidator(10)])

    def __str__(self):
        return f'Username: {self.user.username}'


class ProfileImage(models.Model):
    class Meta:
        verbose_name = 'ProfileImage'
        verbose_name_plural = 'ProfileImages'

    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    image = models.ImageField(upload_to=upload_avatar_profile, null=True, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
