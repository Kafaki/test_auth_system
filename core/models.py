from django.db import models


class BaseModel(models.Model):
    """
    Базовая модель для наследования.
    Для избежания дублирвоания
    """
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

    def __str__(self):
        return f"{self.__class__.__name__}(id={self.id})"


class Role(BaseModel):
    """Роли пользователей: admin, manager, user, guest."""
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name


class BusinessElement(BaseModel):
    """Элементы системы: users, orders, products, ..."""
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name


class AccessRoleRule(BaseModel):
    """Правила доступа для конкретной роли к конкретному бизнес-элементу"""
    role = models.ForeignKey(Role, on_delete=models.CASCADE)
    element = models.ForeignKey(BusinessElement, on_delete=models.CASCADE)

    read_permission = models.BooleanField(default=False)
    read_all_permission = models.BooleanField(default=False)
    create_permission = models.BooleanField(default=False)
    update_permission = models.BooleanField(default=False)
    update_all_permission = models.BooleanField(default=False)
    delete_permission = models.BooleanField(default=False)
    delete_all_permission = models.BooleanField(default=False)

    class Meta:
        unique_together = ('role', 'element')

    def __str__(self):
        return f"{self.role} - {self.element}"
