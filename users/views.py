"""Контроллеры приложения users."""

from rest_framework import generics, mixins, viewsets
from rest_framework.permissions import AllowAny

from users.models import CustomUser, Payment
from users.serializers import PaymentSerializer, UserProfileSerializer, UserRegisterSerializer


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
    """Список, просмотр, редактирование и удаление пользователей."""

    queryset = CustomUser.objects.prefetch_related("payments__paid_course", "payments__paid_lesson")
    serializer_class = UserProfileSerializer


class PaymentListAPIView(generics.ListAPIView):
    """Список платежей с фильтрацией по курсу, уроку, способу оплаты и сортировкой по дате."""

    queryset = Payment.objects.select_related("user", "paid_course", "paid_lesson")
    serializer_class = PaymentSerializer
    filterset_fields = ("paid_course", "paid_lesson", "payment_method")
    ordering_fields = ("payment_date",)
