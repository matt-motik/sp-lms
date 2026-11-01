"""Контроллеры приложения users."""

from typing import Any

from rest_framework import generics, mixins, viewsets
from rest_framework.permissions import AllowAny, BasePermission, IsAuthenticated

from users.models import CustomUser, Payment
from users.permissions import IsProfileOwner
from users.serializers import (
    PaymentSerializer,
    UserProfileSerializer,
    UserPublicSerializer,
    UserRegisterSerializer,
)


class UserRegisterAPIView(generics.CreateAPIView):
    """Регистрация нового пользователя. Доступна без авторизации."""

    queryset = CustomUser.objects.all()
    serializer_class = UserRegisterSerializer
    permission_classes = (AllowAny,)


class UserViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    """Профили пользователей: смотреть можно любой, редактировать и удалять только свой."""

    queryset = CustomUser.objects.prefetch_related("payments__paid_course", "payments__paid_lesson")

    def get_permissions(self) -> list[BasePermission]:
        """Возвращает права для текущего action."""
        if self.action in ("update", "partial_update", "destroy"):
            self.permission_classes = [IsAuthenticated, IsProfileOwner]
        else:
            self.permission_classes = [IsAuthenticated]
        return [permission() for permission in self.permission_classes]

    def is_own_profile(self) -> bool:
        """Проверяет, что запрошен профиль текущего пользователя."""
        return str(self.kwargs.get("pk")) == str(self.request.user.pk)

    def get_serializer_class(self) -> Any:
        """Свой профиль отдаётся полностью, чужой и список — только общая информация."""
        if self.action != "list" and self.is_own_profile():
            return UserProfileSerializer
        return UserPublicSerializer


class PaymentListAPIView(generics.ListAPIView):
    """Список платежей с фильтрацией по курсу, уроку, способу оплаты и сортировкой по дате."""

    queryset = Payment.objects.select_related("user", "paid_course", "paid_lesson")
    serializer_class = PaymentSerializer
    filterset_fields = ("paid_course", "paid_lesson", "payment_method")
    ordering_fields = ("payment_date",)
