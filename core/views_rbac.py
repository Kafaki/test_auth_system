from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from core.models import AccessRoleRule, BusinessElement, Role
from core.serializers import (AccessRoleRuleSerializer,
                              BusinessElementSerializer, RoleSerializer)
from users.mixins import BaseJWTAPIView


def ensure_admin(request):
    """
    Пускаем только пользователя с ролью 'admin'.
    Возвращает Response(403), если нет прав; иначе None.
    """
    user = getattr(request, "user", None)
    role = getattr(user, "role", None)
    if not getattr(user, "id", None) or not role or role.name != "admin":
        return Response({"detail": "Только администратор."}, status=status.HTTP_403_FORBIDDEN)
    return None


class RBACRoleListView(BaseJWTAPIView, APIView):
    """GET /api/rbac/roles/ — список ролей (только admin)"""

    def get(self, request):
        resp = ensure_admin(request)
        if resp:
            return resp
        qs = Role.objects.all().order_by("id")
        return Response(RoleSerializer(qs, many=True).data, status=status.HTTP_200_OK)


class RBACElementListView(BaseJWTAPIView, APIView):
    """GET /api/rbac/elements/ — список элементов (только admin)"""

    def get(self, request):
        resp = ensure_admin(request)
        if resp:
            return resp
        qs = BusinessElement.objects.all().order_by("id")
        return Response(BusinessElementSerializer(qs, many=True).data, status=status.HTTP_200_OK)


class RBACRuleListCreateView(BaseJWTAPIView, APIView):
    """
    GET  /api/rbac/rules/     — список правил (только admin)
    POST /api/rbac/rules/     — создать правило (только admin)
    """

    def get(self, request):
        resp = ensure_admin(request)
        if resp:
            return resp
        qs = AccessRoleRule.objects.select_related("role", "element").order_by("id")
        return Response(AccessRoleRuleSerializer(qs, many=True).data, status=status.HTTP_200_OK)

    def post(self, request):
        resp = ensure_admin(request)
        if resp:
            return resp
        s = AccessRoleRuleSerializer(data=request.data)
        s.is_valid(raise_exception=True)
        rule = s.save()
        return Response(AccessRoleRuleSerializer(rule).data, status=status.HTTP_201_CREATED)


class RBACRuleDetailView(BaseJWTAPIView, APIView):
    """
    GET    /api/rbac/rules/<id>/  — детально (только admin)
    PATCH  /api/rbac/rules/<id>/  — частичное обновление (только admin)
    DELETE /api/rbac/rules/<id>/  — удалить правило (только admin)
    """

    def get(self, request, pk: int):
        resp = ensure_admin(request)
        if resp:
            return resp
        obj = get_object_or_404(AccessRoleRule, pk=pk)
        return Response(AccessRoleRuleSerializer(obj).data, status=status.HTTP_200_OK)

    def patch(self, request, pk: int):
        resp = ensure_admin(request)
        if resp:
            return resp
        obj = get_object_or_404(AccessRoleRule, pk=pk)
        s = AccessRoleRuleSerializer(instance=obj, data=request.data, partial=True)
        s.is_valid(raise_exception=True)
        obj = s.save()
        return Response(AccessRoleRuleSerializer(obj).data, status=status.HTTP_200_OK)

    def delete(self, request, pk: int):
        resp = ensure_admin(request)
        if resp:
            return resp
        obj = get_object_or_404(AccessRoleRule, pk=pk)
        obj.delete()
        return Response({"message": "Правило удалено"}, status=status.HTTP_200_OK)
