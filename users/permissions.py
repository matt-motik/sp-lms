"""Классы прав доступа."""

from typing import Any

from rest_framework.permissions import BasePermission
from rest_framework.request import Request
from rest_framework.views import APIView

MODERATORS_GROUP = "moderators"


class IsModer(BasePermission):
    """Пользователь входит в группу модераторов."""

    message = "Действие доступно только модераторам."

    def has_permission(self, request: Request, view: APIView) -> bool:
        """Проверяет, что пользователь состоит в группе модераторов."""
        user: Any = request.user
        return bool(user and user.is_authenticated and user.groups.filter(name=MODERATORS_GROUP).exists())

    def has_object_permission(self, request: Request, view: APIView, obj: Any) -> bool:
        """Проверяет членство в группе модераторов и на уровне объекта."""
        return self.has_permission(request, view)
