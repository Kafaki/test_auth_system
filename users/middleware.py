from django.utils.deprecation import MiddlewareMixin

from users.models import User
from users.utils import decode_jwt_token


class JWTUserMiddleware(MiddlewareMixin):
    """Определяет request.user по JWT токену."""

    def process_request(self, request):
        # Сбить возможный кэш анонима и стартовать с None
        if hasattr(request, "_cached_user"):
            delattr(request, "_cached_user")
        request.user = None

        # Достаем Authorization: "Bearer <token>"
        auth = request.META.get("HTTP_AUTHORIZATION", "")
        parts = auth.split(" ", 1)
        if len(parts) != 2 or parts[0].lower() != "bearer":
            return

        # Проврка - срез лишних символов
        token = parts[1].strip().strip('"\'')
        if not token:
            return

        # Переводим токен в user_id
        user_id, token_version = decode_jwt_token(token)
        if not user_id:
            return

        # Поиск активного пользователя
        user = User.objects.filter(id=user_id, is_active=True).first()
        if not user:
            return

        # Версия токена устарела
        if user.token_version != token_version:
            return

        # Закидываем найденного пользователя
        request.user = user
        request._cached_user = user
