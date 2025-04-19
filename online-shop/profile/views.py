from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema, OpenApiResponse
from profile.models import Profile
from profile.profile_services import (
    get_profile_or_404,
    update_avatar,
    validate_image_func,
)
from profile.serializers import PasswordSerializer, ProfileSerializer


class APIViewWithAuthentication(APIView):
    """Базовый класс для API представлений с аутентификацией"""

    permission_classes = [IsAuthenticated]
    serializer_class = ProfileSerializer

    _status_response_400 = HTTP_400_BAD_REQUEST
    _status_response_200 = HTTP_200_OK

    def get_profile(self, request: Request) -> Profile:
        """Метод возвращает профиль, или вызывает исключение если он не найден"""

        return get_profile_or_404(request.user)

    def get_profile_serializer(self, profile: Profile) -> ProfileSerializer:
        """Метод возвращает сериализованные данные профиля"""

        serializer = ProfileSerializer(profile, many=False)
        return serializer

    def update_avatar(self, request: Request) -> Response:
        """Метод проверяет аватар, устанавливает его и удаляет старый"""

        validate_result = validate_image_func(request)

        if not validate_result is True:
            return Response(
                {"Error": validate_result}, status=self._status_response_400
            )

        profile = self.get_profile(request)
        update_avatar(profile, request)
        serializer = self.get_profile_serializer(profile).data

        return Response(serializer)


class ProfileView(APIViewWithAuthentication):
    """View для обновления данных пользователя"""

    @extend_schema(
        responses=ProfileSerializer,
        description="Получение данных профиля текущего пользователя"
    )
    def get(self, request):
        profile = self.get_profile(request)
        serializer = self.get_profile_serializer(profile).data
        return Response(serializer)

    @extend_schema(
        request=ProfileSerializer,
        responses={
            200: ProfileSerializer,
            400: OpenApiResponse(description="Ошибка валидации данных")
        },
        description="Обновление данных профиля пользователя или аватара"
    )
    def post(self, request):

        profile = self.get_profile(request)

        if "avatar" in request.FILES:
            return self.update_avatar(request)

        serializer = ProfileSerializer(profile, data=request.data, partial=True)

        if not serializer.is_valid():
            return Response(
                {"Error": serializer.errors}, status=self._status_response_400
            )

        serializer.save()
        serializer = self.get_profile_serializer(serializer.instance).data

        return Response(serializer)


class UpdateAvatarView(APIViewWithAuthentication):
    """View для обновления аватара пользователя"""

    def post(self, request: Request) -> Response:
        if not "avatar" in request.FILES:
            return Response(
                {"Message": "Avatar file was not provided in the request"},
                status=self._status_response_200,
            )

        return self.update_avatar(request)


class UpdatePasswordView(APIViewWithAuthentication):
    """View для изменения пароля пользователя"""

    serializer_class = PasswordSerializer

    @extend_schema(
        request=None,
        responses={
            200: ProfileSerializer,
            400: OpenApiResponse(description="Ошибка валидации изображения"),
        },
        description="Обновление аватара пользователя"
    )
    def post(self, request: Request) -> Response:

        profile = self.get_profile(request)
        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid():
            if not profile.user.check_password(serializer.data.get("currentPassword")):
                return Response(
                    {"Error": "incorrect current password"},
                    status=self._status_response_400,
                )

            profile.user.set_password(serializer.data.get("newPassword"))
            profile.user.save()

            return Response(serializer.data, status=self._status_response_200)
        return Response({"Error": serializer.errors}, status=self._status_response_400)
