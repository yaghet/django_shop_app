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

    """ View представление для регистрации пользователя """

    form_class = RegisterForm

    def post(self, request: Request):
        try:
            user_data = json.loads(request.body)
        except json.JSONDecodeError:
            return Response({"Error": "Invalid JSON"}, status=status.HTTP_400_BAD_REQUEST)

        form = self.form_class(data=user_data)

        if form.is_valid():

            username = user_data.get("username")
            password = user_data.get("password")

            if register_and_login(request, username, password):
                return Response(status=status.HTTP_200_OK)
            else:
                return Response({"Error": "Registration failed"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(form.errors, status=status.HTTP_400_BAD_REQUEST)


class LogoutView(APIView):

    """View представление для выхода пользователя из приложения"""

    def post(self, request: Request):
        logout_user(request)
        return Response(status=status.HTTP_200_OK)
