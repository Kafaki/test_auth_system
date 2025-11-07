# users/management/commands/create_test_users.py
from django.core.management.base import BaseCommand
from django.db import transaction
from users.models import User
from core.models import Role

TEST_USERS = [
    ("admin@test.com", "Admin", "Test123", "admin"),
    ("manager@test.com", "Manager", "Test123", "manager"),
    ("user1@example.com", "User1", "Test123", "user"),
    ("user2@example.com", "User2", "Test123", "user"),
    ("user3@example.com", "User3", "Test123", "user"),
    ("user4@example.com", "User4", "Test123", "guest"),

]


class Command(BaseCommand):
    help = "Создаёт тестовых пользоватлей (admin, manager, user) с ролями."

    @transaction.atomic
    def handle(self, *args, **options):
        created = 0
        for email, first_name, raw_password, role_name in TEST_USERS:
            role = Role.objects.filter(name=role_name).first()
            if not role:
                self.stdout.write(self.style.WARNING(
                    f"Роль '{role_name}' не найдена. Пропуск пользователя {email}."
                ))
                continue

            user, was_created = User.objects.get_or_create(
                email=email,
                defaults={
                    "first_name": first_name,
                    "is_active": True,
                    "role": role,
                },
            )
            if was_created:
                user.set_password(raw_password)
                user.save(update_fields=["password"])
                created += 1
                self.stdout.write(self.style.SUCCESS(
                    f"Создан: {email} (роль: {role_name}, пароль: {raw_password})"
                ))
            else:
                # Обновим роль и активность на всякий случай
                changed = False
                if user.role_id != role.id:
                    user.role = role
                    changed = True
                if not user.is_active:
                    user.is_active = True
                    changed = True
                if changed:
                    user.save(update_fields=["role", "is_active"])
                self.stdout.write(f"Уже существует: {email} (роль: {role_name})")

        self.stdout.write(self.style.SUCCESS(f"Готово. Новых создано: {created}."))
