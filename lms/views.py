"""Контроллеры приложения lms."""

from typing import Any

from django.db.models import QuerySet
from drf_spectacular.utils import OpenApiResponse, extend_schema, extend_schema_view
from rest_framework import generics, status, viewsets
from rest_framework.permissions import BasePermission, IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from config.schema import (
    FORBIDDEN,
    NOT_FOUND,
    UNAUTHORIZED,
    VALIDATION_ERROR,
    MessageSerializer,
    id_parameter,
    ordering_parameter,
)
from lms.models import Course, Lesson, Subscription
from lms.paginators import MaterialsPaginator
from lms.serializers import CourseSerializer, LessonSerializer, SubscriptionSerializer
from users.permissions import IsModer, IsOwner, is_moderator

COURSE_ID = id_parameter("ID курса.")
LESSON_ID = id_parameter("ID урока.")


@extend_schema(tags=["Курсы"])
@extend_schema_view(
    list=extend_schema(
        summary="Список курсов",
        description="Модератор видит все курсы, остальные пользователи — только свои. Вывод постраничный.",
        parameters=[ordering_parameter("Сортировка по полю курса, например id или -id (по убыванию).")],
        responses={200: CourseSerializer(many=True), 401: UNAUTHORIZED},
    ),
    create=extend_schema(
        summary="Создание курса",
        description="Владельцем курса становится текущий пользователь. Модератору недоступно. "
        "В описании допускаются только ссылки на youtube.com.",
        responses={201: CourseSerializer, 400: VALIDATION_ERROR, 401: UNAUTHORIZED, 403: FORBIDDEN},
    ),
    retrieve=extend_schema(
        summary="Просмотр курса",
        description="Доступно владельцу и модератору. Поле is_subscribed — подписан ли текущий пользователь на курс.",
        parameters=[COURSE_ID],
        responses={200: CourseSerializer, 401: UNAUTHORIZED, 403: FORBIDDEN, 404: NOT_FOUND},
    ),
    update=extend_schema(
        summary="Изменение курса",
        description="Доступно владельцу и модератору.",
        parameters=[COURSE_ID],
        responses={200: CourseSerializer, 400: VALIDATION_ERROR, 401: UNAUTHORIZED, 403: FORBIDDEN, 404: NOT_FOUND},
    ),
    partial_update=extend_schema(
        summary="Частичное изменение курса",
        description="Доступно владельцу и модератору.",
        parameters=[COURSE_ID],
        responses={200: CourseSerializer, 400: VALIDATION_ERROR, 401: UNAUTHORIZED, 403: FORBIDDEN, 404: NOT_FOUND},
    ),
    destroy=extend_schema(
        summary="Удаление курса",
        description="Доступно только владельцу, модератору недоступно. Уроки курса удаляются вместе с ним.",
        parameters=[COURSE_ID],
        responses={204: None, 401: UNAUTHORIZED, 403: FORBIDDEN, 404: NOT_FOUND},
    ),
)
class CourseViewSet(viewsets.ModelViewSet):
    """CRUD курсов на основе ViewSet."""

    serializer_class = CourseSerializer
    pagination_class = MaterialsPaginator

    def get_queryset(self) -> QuerySet[Course]:
        """Модератор видит все курсы, остальные пользователи — только свои."""
        # При генерации документации запрос идёт без пользователя
        if getattr(self, "swagger_fake_view", False):
            return Course.objects.none()
        queryset = Course.objects.prefetch_related("lessons")
        if self.action == "list" and not is_moderator(self.request.user):
            queryset = queryset.filter(owner=self.request.user)
        return queryset

    def get_permissions(self) -> list[BasePermission]:
        """Возвращает права для текущего action."""
        if self.action == "create":
            self.permission_classes = [IsAuthenticated, ~IsModer]  # type: ignore[operator]
        elif self.action == "destroy":
            self.permission_classes = [IsAuthenticated, ~IsModer, IsOwner]  # type: ignore[operator]
        elif self.action in ("retrieve", "update", "partial_update"):
            self.permission_classes = [IsAuthenticated, IsModer | IsOwner]  # type: ignore[operator]
        else:
            self.permission_classes = [IsAuthenticated]
        return [permission() for permission in self.permission_classes]

    def perform_create(self, serializer: Any) -> None:
        """Привязывает создаваемый курс к текущему пользователю."""
        serializer.save(owner=self.request.user)


@extend_schema(
    tags=["Уроки"],
    summary="Создание урока",
    description="Владельцем урока становится текущий пользователь. Модератору недоступно. "
    "В video_url и описании допускаются только ссылки на youtube.com.",
    responses={201: LessonSerializer, 400: VALIDATION_ERROR, 401: UNAUTHORIZED, 403: FORBIDDEN},
)
class LessonCreateAPIView(generics.CreateAPIView):
    """Создание урока. Модератору недоступно."""

    serializer_class = LessonSerializer
    permission_classes = [IsAuthenticated, ~IsModer]  # type: ignore[operator]

    def perform_create(self, serializer: Any) -> None:
        """Привязывает создаваемый урок к текущему пользователю."""
        serializer.save(owner=self.request.user)


@extend_schema(
    tags=["Уроки"],
    summary="Список уроков",
    description="Модератор видит все уроки, остальные пользователи — только свои. Вывод постраничный.",
    parameters=[ordering_parameter("Сортировка по полю урока, например id или -id (по убыванию).")],
    responses={200: LessonSerializer(many=True), 401: UNAUTHORIZED},
)
class LessonListAPIView(generics.ListAPIView):
    """Список уроков: модератору все, остальным только свои."""

    serializer_class = LessonSerializer
    pagination_class = MaterialsPaginator
    permission_classes = [IsAuthenticated]

    def get_queryset(self) -> QuerySet[Lesson]:
        """Модератор видит все уроки, остальные пользователи — только свои."""
        if getattr(self, "swagger_fake_view", False):
            return Lesson.objects.none()
        if is_moderator(self.request.user):
            return Lesson.objects.all()
        return Lesson.objects.filter(owner=self.request.user)


@extend_schema(
    tags=["Уроки"],
    summary="Просмотр урока",
    description="Доступно владельцу и модератору.",
    parameters=[LESSON_ID],
    responses={200: LessonSerializer, 401: UNAUTHORIZED, 403: FORBIDDEN, 404: NOT_FOUND},
)
class LessonRetrieveAPIView(generics.RetrieveAPIView):
    """Просмотр урока: модератору или владельцу."""

    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = [IsAuthenticated, IsModer | IsOwner]  # type: ignore[operator]


@extend_schema_view(
    put=extend_schema(summary="Изменение урока"),
    patch=extend_schema(summary="Частичное изменение урока"),
)
@extend_schema(
    tags=["Уроки"],
    description="Доступно владельцу и модератору. В video_url и описании допускаются только ссылки на youtube.com.",
    parameters=[LESSON_ID],
    responses={200: LessonSerializer, 400: VALIDATION_ERROR, 401: UNAUTHORIZED, 403: FORBIDDEN, 404: NOT_FOUND},
)
class LessonUpdateAPIView(generics.UpdateAPIView):
    """Редактирование урока: модератору или владельцу."""

    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = [IsAuthenticated, IsModer | IsOwner]  # type: ignore[operator]


@extend_schema(
    tags=["Уроки"],
    summary="Удаление урока",
    description="Доступно только владельцу, модератору недоступно.",
    parameters=[LESSON_ID],
    request=None,
    responses={204: None, 401: UNAUTHORIZED, 403: FORBIDDEN, 404: NOT_FOUND},
)
class LessonDestroyAPIView(generics.DestroyAPIView):
    """Удаление урока: только владельцу, модератору недоступно."""

    queryset = Lesson.objects.all()
    permission_classes = [IsAuthenticated, ~IsModer, IsOwner]  # type: ignore[operator]


class SubscriptionAPIView(APIView):
    """Подписка на обновления курса: повторный запрос по тому же курсу снимает подписку."""

    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["Подписки"],
        summary="Подписка на курс или отписка",
        description="Если подписки на курс нет — создаёт её и возвращает 201. "
        "Если подписка уже есть — удаляет её и возвращает 200.",
        request=SubscriptionSerializer,
        responses={
            201: OpenApiResponse(MessageSerializer, description="Подписка добавлена."),
            200: OpenApiResponse(MessageSerializer, description="Подписка удалена."),
            400: VALIDATION_ERROR,
            401: UNAUTHORIZED,
        },
    )
    def post(self, request: Request) -> Response:
        """Создаёт подписку, если её нет, и удаляет, если она уже есть."""
        serializer = SubscriptionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        course = serializer.validated_data["course"]

        subscription = Subscription.objects.filter(user=request.user, course=course)
        if subscription.exists():
            subscription.delete()
            return Response({"message": f"Подписка на курс «{course.title}» удалена."}, status=status.HTTP_200_OK)

        Subscription.objects.create(user=request.user, course=course)
        return Response({"message": f"Подписка на курс «{course.title}» добавлена."}, status=status.HTTP_201_CREATED)
