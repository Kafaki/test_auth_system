from rest_framework import serializers

from core.utils.roles import get_default_user_role

from .models import User


class RegisterSerializer(serializers.Serializer):
    first_name = serializers.CharField(max_length=150)
    last_name = serializers.CharField(max_length=150, required=False, allow_blank=True)
    middle_name = serializers.CharField(max_length=150, required=False, allow_blank=True)
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, min_length=6)
    password_repeat = serializers.CharField(write_only=True, min_length=6)

    def validate_email(self, email):
        """Проверка уникального email"""
        email = email.lower().strip()
        if User.objects.filter(email=email).exists():
            raise serializers.ValidationError('Пользователь с таким Email уже существует')
        return email

    def validate_password(self, value):
        """Проверка сложности пароля"""
        if len(value) < 6:
            raise serializers.ValidationError("Пароль должен содержать минимум 6 символов.")
        if value.isdigit() or value.isalpha():
            raise serializers.ValidationError("Пароль должен содержать буквы и цифры.")
        return value

    def validate(self, attrs):
        """Проверка совпадения паролей"""
        if attrs.get("password") != attrs.get("password_repeat"):
            raise serializers.ValidationError("Пароли не совпадают!")
        return attrs

    def create(self, validated_data):
        """Создание пользователя"""
        validated_data.pop("password_repeat")
        password = validated_data.pop("password")
        user = User(**validated_data)
        user.set_password(password)
        user.role = get_default_user_role()
        user.save()
        return user


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, trim_whitespace=False, min_length=6)

    def validate_email(self, email):
        """Приводим полученный email к нижнему регистру и убираем пробелы"""
        return email.lower().strip()

    def validate(self, attrs):
        """Поиск пользователя и проверка пароля"""
        email, password = attrs.get("email"), attrs.get("password")

        try:
            user = User.objects.get(email=email, is_active=True)
        except User.DoesNotExist:
            raise serializers.ValidationError("Неверный email или пароль.")

        if not user.check_password(password):
            raise serializers.ValidationError("Неверный email или пароль.")

        attrs["user"] = user
        return attrs


class ProfileSerializer(serializers.ModelSerializer):
    """Сериализатор профиля"""

    class Meta:
        model = User
        fields = ("id", "email", "first_name", "last_name", "middle_name")
        read_only_fields = ("id", "email")

    def validate(self, attrs):
        """Удаляем пробелы по краям строковых полей."""
        for field, value in attrs.items():
            if isinstance(value, str):
                attrs[field] = value.strip()
        return attrs


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True, min_length=6)
    new_password_repeat = serializers.CharField(write_only=True, min_length=6)

    def validate(self, attrs):
        old = attrs.get("old_password")
        new = attrs.get("new_password")
        new2 = attrs.get("new_password_repeat")

        user = self.context.get("user")
        if not user:
            raise serializers.ValidationError("Пользователь не найден")

        # Проверяем старый пароль
        if not user.check_password(old):
            raise serializers.ValidationError("Старый пароль указан неверно")

        # Совпадают ли новые?
        if new != new2:
            raise serializers.ValidationError("Новые пароли не совпадают")

        # Минимальные требования к паролю
        if new.isalpha() or new.isdigit():
            raise serializers.ValidationError("Пароль должен содержать буквы и цифры")

        return attrs


from rest_framework import serializers

from core.models import Role

from .models import User


class AdminUserCreateSerializer(serializers.Serializer):
    """
    Создание пользователя админом/менеджером.
    User/Guest не пройдут по RBAC в view.
    """
    email = serializers.EmailField()
    first_name = serializers.CharField(max_length=150)
    last_name = serializers.CharField(required=False, allow_blank=True, max_length=150)
    middle_name = serializers.CharField(required=False, allow_blank=True, max_length=150)
    password = serializers.CharField(write_only=True, min_length=6)
    role_id = serializers.IntegerField(required=False, allow_null=True)  # опционально

    def validate_email(self, v):
        v = v.lower().strip()
        if User.objects.filter(email=v).exists():
            raise serializers.ValidationError("Пользователь с таким email уже существует.")
        return v

    def create(self, validated_data):
        role_id = validated_data.pop("role_id", None)
        password = validated_data.pop("password")

        user = User(**validated_data)
        user.set_password(password)

        # если роль не передана — по умолчанию "user"
        if role_id is None:
            try:
                user.role = Role.objects.get(name="user")
            except Role.DoesNotExist:
                user.role = None
        else:
            user.role_id = role_id

        user.save()
        return user


class AdminUserUpdateSerializer(serializers.ModelSerializer):
    """
    Обновление профиля админом/менеджером (Update_all у менеджера есть).

    """
    class Meta:
        model = User
        fields = ("first_name", "last_name", "middle_name", "is_active", "role")
        extra_kwargs = {
            "is_active": {"required": False},
            "role": {"required": False},
        }