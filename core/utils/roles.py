from core.models import Role

DEFAULT_USER_ROLE_NAME = "user"

def get_default_user_role():
    """
    Возвращает объект роли 'user'.
    Если её нет в базе — создаёт с описанием 'Обычный пользователь'.
    """
    role, _ = Role.objects.get_or_create(
        name=DEFAULT_USER_ROLE_NAME,
        defaults={"description": "Обычный пользователь"},
    )
    return role