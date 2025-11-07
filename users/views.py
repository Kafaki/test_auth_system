from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from core.mixins import AccessControlMixin
from users.models import User

from .mixins import BaseJWTAPIView
from .serializers import (AdminUserCreateSerializer, AdminUserUpdateSerializer,
                          ChangePasswordSerializer, LoginSerializer,
                          ProfileSerializer, RegisterSerializer)
from .utils import create_jwt_token


class RegistrationView(APIView):
    """
    Регистрация нового пользователя
    """

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response(
                {
                    "message": "Пользователь успешно зарегистрирован",
                    "user": {
                        "id": user.id,
                        "email": user.email,
                        "first_name": user.first_name,
                        "last_name": user.last_name,
                    },
                },
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    """
    Вход по email и паролю. Возвращает JWT-токен и базовые данные пользователя.
    """

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data["user"]
        user.up_token_version()
        token = create_jwt_token(user)

        return Response(
            {
                "access_token": token,
                "token_type": "Bearer",
                "user": {
                    "id": user.id,
                    "email": user.email,
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                },
            },
            status=status.HTTP_200_OK,
        )


class ProfileView(BaseJWTAPIView):
    """GET — профиль; PATCH — частичное обновление профиля."""

    def get(self, request):
        user = self.current_user(request)
        if not getattr(user, "id", None):
            return Response({"detail": "Не авторизован"}, status=status.HTTP_401_UNAUTHORIZED)
        return Response(ProfileSerializer(user).data, status=status.HTTP_200_OK)

    def patch(self, request):
        user = self.current_user(request)
        if not getattr(user, "id", None):
            return Response({"detail": "Не авторизован"}, status=status.HTTP_401_UNAUTHORIZED)
        s = ProfileSerializer(instance=user, data=request.data, partial=True)
        s.is_valid(raise_exception=True)
        user = s.save()
        return Response(ProfileSerializer(user).data, status=status.HTTP_200_OK)


class ChangePasswordView(BaseJWTAPIView):
    """
    Смена пароля пользователя.

    """

    def post(self, request):
        user = self.current_user(request)
        if not getattr(user, "id", None):
            return Response({"detail": "Не авторизован"}, status=status.HTTP_401_UNAUTHORIZED)

        serializer = ChangePasswordSerializer(
            data=request.data,
            context={"user": user}
        )
        serializer.is_valid(raise_exception=True)

        # Меняем пароль
        new_pass = serializer.validated_data["new_password"]
        user.set_password(new_pass)
        user.save()

        # инвалидация выданного токена
        user.up_token_version()

        return Response({"message": "Пароль успешно изменён"}, status=status.HTTP_200_OK)


class LogoutView(BaseJWTAPIView):
    """
    Logout: становятся недействительными ВСЕ текущие JWT токены пользователя
    путём увеличения user.token_version.
    """

    def post(self, request):
        user = request.user
        if not getattr(user, "id", None):
            return Response({"detail": "Не авторизован"}, status=status.HTTP_401_UNAUTHORIZED)

        # Инвалидация токенов: просто увеличиваем версию
        user.up_token_version()

        return Response(
            {"message": "Вы вышли из системы. Все ранее выданные токены аннулированы."},
            status=status.HTTP_200_OK,
        )


class SoftDeactivateMeView(BaseJWTAPIView):
    """
    Мягкое удаление аккаунта самим пользователем.
    После вызова — токены становятся невалидными, логин невозможен.
    """

    def post(self, request):
        user = self.current_user(request)
        if not getattr(user, "id", None):
            return Response({"detail": "Не авторизован"}, status=status.HTTP_401_UNAUTHORIZED)

        # Деактивируем
        user.deactivate()

        return Response(
            {"message": "Аккаунт деактивирован. Все сессии завершены."},
            status=status.HTTP_200_OK
        )
