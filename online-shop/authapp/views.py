import json
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from rest_framework.request import Request
from authapp.auth_services import (authenticate_and_login, register_and_login, logout_user)

from authapp.forms import RegisterForm


class LoginView(APIView):

    """View представления для входа в приложение"""

    def post(self, request: Request):

        body = json.loads(request.body)

        username = body['username']
        password = body['password']

        if authenticate_and_login(request, username, password):
            return Response(status=status.HTTP_200_OK)
        return Response(status=status.HTTP_401_UNAUTHORIZED)


class RegisterView(APIView):

    """View представление для регистрации пользователя"""

    form_class = RegisterForm

    def post(self, request: Request):

        form = self.form_class(data=request.data)

        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']

            if register_and_login(request, username, password):
                return Response(status=status.HTTP_200_OK)
            else:
                return Response(status=status.HTTP_401_UNAUTHORIZED)
        else:
            raise ValidationError(form.errors)


class LogoutView(APIView):

    """View представление для выхода пользователя из приложения"""

    def post(self, request: Request):
        logout_user(request)
        return Response(status=status.HTTP_200_OK)
