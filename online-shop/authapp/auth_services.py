import json

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from rest_framework.request import Request

from profileapp.models import Profile


def login_user(request: Request, user):
    """Функция выполняет вход пользователя в приложение"""
    login(request, user)


def logout_user(request: Request):
    """Функция выполняет выход пользователя в приложение"""
    logout(request)


def create_user(username: str, password: str, full_name: str):
    """Функция создаёт новый профиль и связывает его с User"""
    user = User.objects.create_user(username=username, password=password)
    Profile.objects.create(user=user, fullName=full_name)
    return user


def authenticate_and_login(request: Request, username: str, password: str):
    """Функция выполняет аутентификацию и логинит пользователя"""
    user = authenticate(request, username=username, password=password)
    if user is not None:
        login_user(request, user)
        return True
    return False


def register_and_login(request: Request, username: str, password: str, full_name: str):
    """Функция выполняет регистрацию и логинит пользователя"""
    create_user(username=username, password=password, full_name=full_name)
    return authenticate_and_login(request, username, password)


def load_json(body):
    try:
        return json.loads(body)
    except json.JSONDecodeError:
        raise ValueError("Invalid JSON")


def get_data_from_body(body):

    username = body['username']
    password = body['password']

    if 'name' in body:
        full_name = body['name']
        return username, password, full_name

    return username, password
