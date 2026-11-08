"""Контроллеры приложения users."""

from typing import Any

from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import (
    OpenApiParameter,
    OpenApiResponse,
    PolymorphicProxySerializer,
    extend_schema,
    extend_schema_view,
    inline_serializer,
)
from rest_framework import generics, mixins, serializers, viewsets
from rest_framework.permissions import AllowAny, BasePermission, IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from config.schema import FORBIDDEN, NOT_FOUND, UNAUTHORIZED, VALIDATION_ERROR, id_parameter, ordering_parameter
from users.models import CustomUser, Payment
from users.permissions import IsProfileOwner
from users.serializers import (
    PaymentSerializer,
    UserProfileSerializer,
    UserPublicSerializer,
    UserRegisterSerializer,
)


@extend_schema(
    tags=["Пользователи"],
    summary="Регистрация",
    description="Доступна без авторизации. Email должен быть свободен, пароль проверяется валидаторами Django.",
    responses={201: UserRegisterSerializer, 400: VALIDATION_ERROR},
)
class UserRegisterAPIView(generics.CreateAPIView):
    """Регистрация нового пользователя. Доступна без авторизации."""

    queryset = CustomUser.objects.all()
    serializer_class = UserRegisterSerializer
    permission_classes = (AllowAny,)


@extend_schema(
    tags=["Авторизация"],
    summary="Получение токенов",
    description="Возвращает пару access / refresh по email и паролю. Доступно без авторизации.",
    responses={
        200: inline_serializer(
            name="TokenPair",
            fields={"access": serializers.CharField(), "refresh": serializers.CharField()},
        ),
        400: VALIDATION_ERROR,
        401: OpenApiResponse(description="Неверный email или пароль."),
    },
)
class UserTokenObtainPairView(TokenObtainPairView):
    """Получение пары JWT-токенов. Доступно без авторизации."""


@extend_schema(
    tags=["Авторизация"],
    summary="Обновление access-токена",
    description="Возвращает новый access по refresh-токену. Доступно без авторизации.",
    responses={
        200: inline_serializer(name="AccessToken", fields={"access": serializers.CharField()}),
        400: VALIDATION_ERROR,
        401: OpenApiResponse(description="Refresh-токен недействителен или истёк."),
    },
)
class UserTokenRefreshView(TokenRefreshView):
    """Обновление access-токена по refresh. Доступно без авторизации."""


USER_ID = id_parameter("ID пользователя.")

UserProfileOrPublic = PolymorphicProxySerializer(
    component_name="UserProfileOrPublic",
    serializers=[UserProfileSerializer, UserPublicSerializer],
    resource_type_field_name=None,
)


@extend_schema(tags=["Пользователи"])
@extend_schema_view(
    list=extend_schema(
        summary="Список пользователей",
        description="Только общая информация: без фамилии и платежей.",
        parameters=[ordering_parameter("Сортировка по полю пользователя, например id или -id (по убыванию).")],
        responses={200: UserPublicSerializer(many=True), 401: UNAUTHORIZED},
    ),
    retrieve=extend_schema(
        summary="Профиль пользователя",
        parameters=[USER_ID],
        description="Свой профиль отдаётся полностью, с фамилией и историей платежей. "
        "Чужой — только общая информация.",
        responses={200: UserProfileOrPublic, 401: UNAUTHORIZED, 404: NOT_FOUND},
    ),
    update=extend_schema(
        summary="Изменение своего профиля",
        parameters=[USER_ID],
        description="Редактировать можно только свой профиль.",
        request=UserProfileSerializer,
        responses={
            200: UserProfileSerializer,
            400: VALIDATION_ERROR,
            401: UNAUTHORIZED,
            403: FORBIDDEN,
            404: NOT_FOUND,
        },
    ),
    partial_update=extend_schema(
        summary="Частичное изменение своего профиля",
        parameters=[USER_ID],
        description="Редактировать можно только свой профиль.",
        request=UserProfileSerializer,
        responses={
            200: UserProfileSerializer,
            400: VALIDATION_ERROR,
            401: UNAUTHORIZED,
            403: FORBIDDEN,
            404: NOT_FOUND,
        },
    ),
    destroy=extend_schema(
        summary="Удаление своего профиля",
        parameters=[USER_ID],
        description="Удалить можно только свой профиль.",
        responses={204: None, 401: UNAUTHORIZED, 403: FORBIDDEN, 404: NOT_FOUND},
    ),
)
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


@extend_schema(
    tags=["Платежи"],
    summary="Список платежей",
    description="Фильтрация по курсу, уроку и способу оплаты, сортировка по дате оплаты.",
    parameters=[
        OpenApiParameter("paid_course", OpenApiTypes.INT, description="ID оплаченного курса."),
        OpenApiParameter("paid_lesson", OpenApiTypes.INT, description="ID оплаченного урока."),
        OpenApiParameter(
            "payment_method",
            OpenApiTypes.STR,
            description="Способ оплаты: cash — наличные, transfer — перевод на счёт.",
            enum=Payment.PaymentMethod.values,
        ),
        ordering_parameter(
            "Сортировка по дате оплаты: payment_date — по возрастанию, -payment_date — по убыванию.",
            ("payment_date",),
        ),
    ],
    responses={200: PaymentSerializer(many=True), 401: UNAUTHORIZED},
)
class PaymentListAPIView(generics.ListAPIView):
    """Список платежей с фильтрацией по курсу, уроку, способу оплаты и сортировкой по дате."""

    queryset = Payment.objects.select_related("user", "paid_course", "paid_lesson")
    serializer_class = PaymentSerializer
    filterset_fields = ("paid_course", "paid_lesson", "payment_method")
    ordering_fields = ("payment_date",)
