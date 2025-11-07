import bcrypt
from django.db import models

from core.models import BaseModel, Role


class User(BaseModel):
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150, blank=True, null=True)
    middle_name = models.CharField(max_length=150, blank=True, null=True)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=300)
    is_active = models.BooleanField(default=True)
    token_version = models.PositiveIntegerField(default=0)
    role = models.ForeignKey(Role, on_delete=models.SET_NULL, related_name="users", null=True, blank=True)

    def set_password(self, raw_password: str):
        """Хэширование пароля по алгоритму bcrypt"""
        hashes = bcrypt.hashpw(raw_password.encode('utf-8'), bcrypt.gensalt())
        self.password = hashes.decode('utf-8')

    def check_password(self, raw_password: str) -> bool:
        """Проверка пароля"""
        return bcrypt.checkpw(raw_password.encode('utf-8'), self.password.encode('utf-8'))

    def deactivate(self):
        """'Мягкое' удаление"""
        self.is_active = False
        self.up_token_version()
        self.save(update_fields=["is_active", "token_version"])

    def up_token_version(self):
        self.token_version += 1
        self.save(update_fields=["token_version"])

    def save(self, *args, **kwargs):
        """
        Защита от случайного сохранения незахэшированного пароля.
        Пароль хэшируется через set_password() перед сохранением, но
        через shell можно напрямую создать экземпляр без хэшпароля.
        """
        bcrypt_prefixes = ("$2b$", "$2y$", "$2a$")
        if not any(self.password.startswith(prefix) for prefix in bcrypt_prefixes):
            # если поле password не похоже на bcrypt-хэш — хэшируем
            self.set_password(self.password)
        super().save(*args, **kwargs)

    def __str__(self):
        status = "активен" if self.is_active else "не активен"
        return f"Пользователь {self.email} ({status})"
