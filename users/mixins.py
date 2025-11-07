from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView


class CsrfExemptMixin:
    """Отключаем CSRF для API-вью (мы используем JWT, а не cookie-сессии)."""
    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)


class JwtRequestUserMixin:
    """
    Протаскиваем user, установленный в middleware, в DRF Request.
    Без этого DRF видит AnonymousUser.
    """
    def initialize_request(self, request, *args, **kwargs):
        # Создание DRF Request через родительский метод
        drf_req = super().initialize_request(request, *args, **kwargs)
        # пользователь, поставленный в middleware
        django_user = getattr(request, "user", None)
        if django_user is not None:
            # _user — положим туда реального пользователя
            drf_req._user = django_user
        return drf_req

    def current_user(self, request):
        """На всякий случай: отдаём пользователя из DRF Request (уже протянутого из middleware)."""
        return getattr(request, "user", None)


class BaseJWTAPIView(CsrfExemptMixin, JwtRequestUserMixin, APIView):
    """
    Базовый класс:
    - auth/permissions DRF отключены (валидируем сами по request.user),
    - CSRF выключен,
    - user протянут из middleware.
    """
    authentication_classes = []
    permission_classes = [AllowAny]