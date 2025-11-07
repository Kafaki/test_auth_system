from core.models import AccessRoleRule
from users.models import User


def check_permission(
        user: User,
        element_name: str,
        action: str,
        *,
        is_owner: bool = False
) -> bool:
    """Проверяет права доступа пользователя к бизнес-элементу"""
    # ищем правило, которое подходит под роль пользователя и элемент
    rule = AccessRoleRule.objects.filter(role_id=user.role_id, element__name=element_name).first()

    # если нет — сразу False
    if not rule:
        return False

    if action == "create":
        return bool(rule.create_permission)
    # берём из правила нужные флаги
    all_flag = getattr(rule, f"{action}_all_permission", False)
    own_flag = getattr(rule, f"{action}_permission", False)

    # Доступ разрешён если:
    # - разрешено для всех объектов ИЛИ
    # - разрешено для своих объектов И пользователь является владельцем
    return bool(all_flag or (is_owner and own_flag))
