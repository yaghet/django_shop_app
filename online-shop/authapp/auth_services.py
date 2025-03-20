from django.contrib.auth.models import User
from django.contrib.auth import login, logout, authenticate
from profileapp.models import Profile
from rest_framework.request import Request


def login_user(request: Request, user):
    """Функция выполняет вход пользователя в приложение"""
    login(request, user)


def logout_user(request: Request):
    """Функция выполняет выход пользователя в приложение"""
    logout(request)


def create_user(username: str, password: str):
    """Функция создаёт новый профиль и связывает его с User"""
    user = User.objects.create_user(username=username, password=password)
    Profile.objects.create(user=user)
    return user


def authenticate_and_login(request: Request, username: str, password: str):
    """Функция выполняет аутентификацию и логинит пользователя"""
    user = authenticate(request, username=username, password=password)
    if user is not None:
        login_user(request, user)
        return True
    return False


def register_and_login(request: Request, username: str, password: str):
    """Функция выполняет регистрацию и логинит пользователя"""
    create_user(username=username, password=password)
    return authenticate_and_login(request, username, password)