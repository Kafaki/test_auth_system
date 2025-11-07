"""
Файл с jwt токенами

"""

from datetime import UTC, datetime, timedelta

import jwt
from django.conf import settings

from users.models import User

# Настройки токенов (позже вынесу в .env)
JWT_SECRET = getattr(settings, "SECRET_KEY", "default_secret")
JWT_ALGORITHM = "HS256"
JWT_EXP_DELTA_HOURS = 24


def create_jwt_token(user: User) -> str:
    """
    Создание JWT-токена для пользователя.

    payload (полезная нагрузка):
      user_id: идентификатор пользователя;
      v: версия токена
      iat (issued at): время выпуска токена;
      exp (expiration): время истечения действия токена.

    """
    payload = {
        "user_id": user.id,
        "v": user.token_version,
        "iat": datetime.now(UTC),
        "exp": datetime.now(UTC) + timedelta(hours=JWT_EXP_DELTA_HOURS),
    }
    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return token


def decode_jwt_token(token: str) -> tuple[int, int] | None:
    """
    Проверка JWT-токена и извлечение user_id.
    Возвращает None, если токен истёк или некорректен.
    """
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        user_id = int(payload["user_id"])
        token_version = int(payload["v"])
        return user_id, token_version
    except jwt.ExpiredSignatureError:
        # Токен просрочен
        return None
    except jwt.InvalidTokenError:
        # Токен некорректен
        return None