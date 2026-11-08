"""Общие описания ответов для документации API."""

from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, OpenApiResponse, inline_serializer
from rest_framework import serializers

ErrorSerializer = inline_serializer(name="Error", fields={"detail": serializers.CharField()})
MessageSerializer = inline_serializer(name="Message", fields={"message": serializers.CharField()})

VALIDATION_ERROR = OpenApiResponse(
    response=OpenApiTypes.OBJECT,
    description="Ошибка валидации: словарь вида {поле: [сообщения об ошибках]}.",
)
UNAUTHORIZED = OpenApiResponse(response=ErrorSerializer, description="Токен не передан или недействителен.")
FORBIDDEN = OpenApiResponse(response=ErrorSerializer, description="Недостаточно прав для действия.")
NOT_FOUND = OpenApiResponse(response=ErrorSerializer, description="Объект не найден.")
STRIPE_ERROR = OpenApiResponse(
    response=ErrorSerializer,
    description="Ошибка платёжного сервиса Stripe: сервис недоступен или отклонил запрос.",
)


def id_parameter(description: str) -> OpenApiParameter:
    """Описание ID объекта в пути запроса."""
    return OpenApiParameter("id", OpenApiTypes.INT, OpenApiParameter.PATH, description=description)


def ordering_parameter(description: str, fields: tuple[str, ...] | None = None) -> OpenApiParameter:
    """Описание параметра сортировки; fields — допустимые значения, если их список ограничен."""
    enum = [prefix + field for field in fields for prefix in ("", "-")] if fields else None
    return OpenApiParameter("ordering", OpenApiTypes.STR, description=description, enum=enum)
