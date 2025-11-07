# premisions
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.response import Response

from core.mixins import AccessControlMixin
from users.mixins import BaseJWTAPIView
from users.models import User
from users.serializers import (AdminUserCreateSerializer,
                               AdminUserUpdateSerializer)


class AdminUserListCreateView(BaseJWTAPIView, AccessControlMixin):
    """
    GET:
      - admin/manager: видят всех (read_all)
      - user: видит только себя (read own)
      - guest: 403
    POST:
      - admin/manager: можно (create)
      - user/guest: 403
    """
    element_name = "users"

    def get(self, request):
        scope, resp = self.check_read_scope(request)
        if resp:
            return resp

        if scope == "all":
            qs = User.objects.all()
        else:
            qs = User.objects.filter(id=request.user.id)

        data = [
            {
                "id": u.id,
                "email": u.email,
                "first_name": u.first_name,
                "last_name": u.last_name,
                "middle_name": u.middle_name,
                "is_active": u.is_active,
                "role_id": u.role_id,
            }
            for u in qs
        ]
        return Response(data, status=status.HTTP_200_OK)

    def post(self, request):
        # RBAC: create разрешён admin/manager
        resp = self.check_action_permission(request, action="create")
        if resp:
            return resp

        s = AdminUserCreateSerializer(data=request.data)
        s.is_valid(raise_exception=True)
        user = s.save()
        return Response(
            {
                "id": user.id,
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "middle_name": user.middle_name,
                "is_active": user.is_active,
                "role_id": user.role_id,
            },
            status=status.HTTP_201_CREATED,
        )


class AdminUserDetailView(BaseJWTAPIView, AccessControlMixin):
    """
    GET  /admin/users/<id>/ : read / read_all
    PATCH /admin/users/<id>/ : update / update_all
    DELETE /admin/users/<id>/ : delete / delete_all (у менеджера нет)
    """
    element_name = "users"

    def _is_owner(self, request, target: User) -> bool:
        return target.id == request.user.id

    def get(self, request, pk: int):
        target = get_object_or_404(User, pk=pk)
        is_owner = self._is_owner(request, target)

        resp = self.check_action_permission(request, action="read", is_owner=is_owner)
        if resp:
            return resp

        data = {
            "id": target.id,
            "email": target.email,
            "first_name": target.first_name,
            "last_name": target.last_name,
            "middle_name": target.middle_name,
            "is_active": target.is_active,
            "role_id": target.role_id,
        }
        return Response(data, status=status.HTTP_200_OK)

    def patch(self, request, pk: int):
        """Обновление полей доступно только admin/manager"""
        target = get_object_or_404(User, pk=pk)
        is_owner = self._is_owner(request, target)

        # RBAC: admin/manager — да; user — нет
        resp = self.check_action_permission(request, action="update", is_owner=is_owner)
        if resp:
            return resp

        s = AdminUserUpdateSerializer(instance=target, data=request.data, partial=True)
        s.is_valid(raise_exception=True)
        user = s.save()
        return Response(
            {
                "id": user.id,
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "middle_name": user.middle_name,
                "is_active": user.is_active,
                "role_id": user.role_id,
            },
            status=status.HTTP_200_OK,
        )


    def delete(self, request, pk: int):
        """Удаление доступен только с ролью 'admin'"""
        target = get_object_or_404(User, pk=pk)
        is_owner = self._is_owner(request, target)

        # RBAC: удалять может только admin (delete_all=True). manager/user — 403.
        resp = self.check_action_permission(request, action="delete", is_owner=is_owner)
        if resp:
            return resp

        target.deactivate()
        return Response({"message": "Пользователь деактивирован"}, status=status.HTTP_200_OK)