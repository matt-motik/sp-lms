"""Классы прав доступа."""

from typing import Any

from rest_framework.permissions import BasePermission
from rest_framework.request import Request
from rest_framework.views import APIView

MODERATORS_GROUP = "moderators"


def is_moderator(user: Any) -> bool:
    """Возвращает True, если пользователь авторизован и входит в группу модераторов."""
    return bool(user and user.is_authenticated and user.groups.filter(name=MODERATORS_GROUP).exists())


class IsModer(BasePermission):
    """Пользователь входит в группу модераторов."""

    message = "Действие доступно только модераторам."

    def has_permission(self, request: Request, view: APIView) -> bool:
        """Проверяет, что пользователь состоит в группе модераторов."""
        return is_moderator(request.user)

    def has_object_permission(self, request: Request, view: APIView, obj: Any) -> bool:
        """Проверяет членство в группе модераторов и на уровне объекта."""
        return self.has_permission(request, view)


class IsOwner(BasePermission):
    """Пользователь является владельцем объекта."""

    message = "Действие доступно только владельцу."

    def has_object_permission(self, request: Request, view: APIView, obj: Any) -> bool:
        """Проверяет, что объект принадлежит текущему пользователю."""
        return bool(obj.owner == request.user)


class IsProfileOwner(BasePermission):
    """Пользователь работает со своим профилем."""

    message = "Редактировать и удалять можно только свой профиль."

    def has_object_permission(self, request: Request, view: APIView, obj: Any) -> bool:
        """Проверяет, что профиль принадлежит текущему пользователю."""
        return bool(obj == request.user)
