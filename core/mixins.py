from rest_framework import status
from rest_framework.response import Response

from core.permissions import check_permission


class AccessControlMixin:
    """
    Миксин для проверки прав доступа пользователя к бизнес-элементам.
    Использует функцию check_permission() из core/permissions.py.
    """

    element_name = None  # название бизнес-объекта (например, "users", "products" и т.п.)

    def check_read_scope(self, request):
        """
        Проверяет, какие данные пользователь может читать (для списков).

        Возвращает кортеж (scope, resp):
          • scope — тип доступа:
              - "all"       → можно читать все объекты;
              - "own_only"  → можно читать только свои (is_owner=True);
              - None        → если доступа нет.
          • resp — HTTP-ответ:
              - None        → всё ок, можно продолжать;
              - Response(...) → готовый ответ с ошибкой 401 или 403.

        Пример:
            scope, resp = self.check_read_scope(request)
            if resp:
                return resp
        """
        user = getattr(request, "user", None)
        if not getattr(user, "id", None):
            return None, Response({"detail": "Не авторизован"}, status=status.HTTP_401_UNAUTHORIZED)

        # Проверка: может ли читать всё
        if check_permission(user, self.element_name, "read", is_owner=False):
            return "all", None

        # Проверка: может ли читать только свои
        if check_permission(user, self.element_name, "read", is_owner=True):
            return "own_only", None

        # Иначе — доступ запрещён
        return None, Response({"detail": "Доступ запрещён"}, status=status.HTTP_403_FORBIDDEN)

    def check_action_permission(self, request, *, action: str, is_owner: bool = False):
        """
        Проверяет, можно ли пользователю выполнить действие (create, update, delete).

        Возвращает:
          • None — если доступ разрешён (можно продолжать выполнение view);
          • Response(...) — готовый HTTP-ответ с ошибкой 401 (не авторизован)
            или 403 (нет прав).

        Аргументы:
          • action — одно из действий: "create", "read", "update", "delete";
          • is_owner — True, если объект принадлежит пользователю (нужно
            для проверки *_permission вместо *_all_permission).

        Пример:
            resp = self.check_action_permission(request, action="delete", is_owner=True)
            if resp:
                return resp  # вернёт 401 или 403, если доступ запрещён
        """
        user = getattr(request, "user", None)
        if not getattr(user, "id", None):
            return Response({"detail": "Не авторизован"}, status=status.HTTP_401_UNAUTHORIZED)

        # Проверяем права
        if not check_permission(user, self.element_name, action, is_owner=is_owner):
            return Response({"detail": "Доступ запрещён"}, status=status.HTTP_403_FORBIDDEN)

        return None
