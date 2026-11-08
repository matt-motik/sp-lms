"""Контроллеры приложения lms."""

from typing import Any

from django.db.models import QuerySet
from rest_framework import generics, status, viewsets
from rest_framework.permissions import BasePermission, IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from lms.models import Course, Lesson, Subscription
from lms.serializers import CourseSerializer, LessonSerializer, SubscriptionSerializer
from users.permissions import IsModer, IsOwner, is_moderator


class CourseViewSet(viewsets.ModelViewSet):
    """CRUD курсов на основе ViewSet."""

    serializer_class = CourseSerializer

    def get_queryset(self) -> QuerySet[Course]:
        """Модератор видит все курсы, остальные пользователи — только свои."""
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


class LessonCreateAPIView(generics.CreateAPIView):
    """Создание урока. Модератору недоступно."""

    serializer_class = LessonSerializer
    permission_classes = [IsAuthenticated, ~IsModer]  # type: ignore[operator]

    def perform_create(self, serializer: Any) -> None:
        """Привязывает создаваемый урок к текущему пользователю."""
        serializer.save(owner=self.request.user)


class LessonListAPIView(generics.ListAPIView):
    """Список уроков: модератору все, остальным только свои."""

    serializer_class = LessonSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self) -> QuerySet[Lesson]:
        """Модератор видит все уроки, остальные пользователи — только свои."""
        if is_moderator(self.request.user):
            return Lesson.objects.all()
        return Lesson.objects.filter(owner=self.request.user)


class LessonRetrieveAPIView(generics.RetrieveAPIView):
    """Просмотр урока: модератору или владельцу."""

    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = [IsAuthenticated, IsModer | IsOwner]  # type: ignore[operator]


class LessonUpdateAPIView(generics.UpdateAPIView):
    """Редактирование урока: модератору или владельцу."""

    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = [IsAuthenticated, IsModer | IsOwner]  # type: ignore[operator]


class LessonDestroyAPIView(generics.DestroyAPIView):
    """Удаление урока: только владельцу, модератору недоступно."""

    queryset = Lesson.objects.all()
    permission_classes = [IsAuthenticated, ~IsModer, IsOwner]  # type: ignore[operator]


class SubscriptionAPIView(APIView):
    """Подписка на обновления курса: повторный запрос по тому же курсу снимает подписку."""

    permission_classes = [IsAuthenticated]

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
