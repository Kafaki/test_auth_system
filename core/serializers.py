from rest_framework import serializers

from core.models import AccessRoleRule, BusinessElement, Role


class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = ("id", "name", "description", "created_at", "updated_at")


class BusinessElementSerializer(serializers.ModelSerializer):
    class Meta:
        model = BusinessElement
        fields = ("id", "name", "description", "created_at", "updated_at")


class AccessRoleRuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = AccessRoleRule
        fields = (
            "id", "role", "element",
            "read_permission", "read_all_permission",
            "create_permission",
            "update_permission", "update_all_permission",
            "delete_permission", "delete_all_permission",
        )

    def validate(self, attrs):
        # Защитимся от дублей: (role, element) должны быть уникальными
        role = attrs.get("role") or getattr(self.instance, "role", None)
        element = attrs.get("element") or getattr(self.instance, "element", None)
        if role and element:
            qs = AccessRoleRule.objects.filter(role=role, element=element)
            if self.instance:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise serializers.ValidationError("Правило для этой роли и элемента уже существует.")
        return attrs
