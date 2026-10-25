"""Контроллеры приложения users."""

from rest_framework import generics

from users.models import CustomUser, Payment
from users.serializers import PaymentSerializer, UserProfileSerializer


class UserProfileAPIView(generics.RetrieveUpdateAPIView):
    """Просмотр и редактирование профиля любого пользователя с историей платежей."""

    queryset = CustomUser.objects.prefetch_related("payments__paid_course", "payments__paid_lesson")
    serializer_class = UserProfileSerializer


class PaymentListAPIView(generics.ListAPIView):
    """Список платежей с фильтрацией по курсу, уроку, способу оплаты и сортировкой по дате."""

    queryset = Payment.objects.select_related("user", "paid_course", "paid_lesson")
    serializer_class = PaymentSerializer
    filterset_fields = ("paid_course", "paid_lesson", "payment_method")
    ordering_fields = ("payment_date",)
