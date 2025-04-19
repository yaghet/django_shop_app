from drf_spectacular.utils import extend_schema
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.status import (HTTP_200_OK, HTTP_400_BAD_REQUEST,
                                   HTTP_401_UNAUTHORIZED)
from rest_framework.views import APIView

from authapp.auth_services import (authenticate_and_login, get_data_from_body,
                                   load_json, logout_user, register_and_login)
from authapp.serializers import (LogoutSerializer, UserLoginSerializer,
                                 UserRegistrationSerializer)
from rest_framework.permissions import AllowAny


class BaseAuthView(APIView):
    """Базовая форма для регистрации и аутентификации в API"""

    _status_response_200 = HTTP_200_OK
    _status_response_400 = HTTP_400_BAD_REQUEST
    _status_response_401 = HTTP_401_UNAUTHORIZED

    def load_json(self, request: Request):
        try:
            return load_json(body=request.body)
        except ValueError as exp:
            return Response({"Error": str(exp)}, status=self._status_response_400)


@extend_schema(tags=["Auth"])
class LoginView(BaseAuthView):
    """View представления для аутентификации пользователя (войти в приложение)"""

    permission_classes = [AllowAny]
    serializer_class = UserLoginSerializer

    def post(self, request: Request):

        user_data = self.load_json(request)
        serializer = self.serializer_class(data=user_data)
        if serializer.is_valid():
            username, password = get_data_from_body(user_data)

            if authenticate_and_login(request, username, password):
                return Response(status=self._status_response_200)

            return Response(status=self._status_response_401)
        else:
            return Response(
                {"Error": serializer.errors}, status=self._status_response_401
            )


@extend_schema(tags=["Auth"])
class RegisterView(BaseAuthView):
    """View представление для регистрации пользователя"""

    permission_classes = [AllowAny]
    serializer_class = UserRegistrationSerializer

    def post(self, request: Request):

        user_data = self.load_json(request)
        serializer = self.serializer_class(data=user_data)

        if serializer.is_valid():
            username, password, full_name = get_data_from_body(body=user_data)

            if register_and_login(request, username, password, full_name):
                return Response(status=self._status_response_200)
            else:
                return Response(
                    {"Error": "Registration failed"}, status=self._status_response_401
                )
        else:
            return Response(serializer.errors, status=self._status_response_401)


@extend_schema(tags=["Auth"])
class LogoutView(APIView):
    """View представление для выхода пользователя из приложения"""

    serializer_class = LogoutSerializer

    def post(self, request: Request):
        logout_user(request)
        return Response(status=HTTP_200_OK)
