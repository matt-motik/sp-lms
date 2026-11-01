"""Контроллеры приложения lms."""

from rest_framework import generics, viewsets
from rest_framework.permissions import BasePermission, IsAuthenticated

from lms.models import Course, Lesson
from lms.serializers import CourseSerializer, LessonSerializer
from users.permissions import IsModer


class CourseViewSet(viewsets.ModelViewSet):
    """CRUD курсов на основе ViewSet."""

    queryset = Course.objects.prefetch_related("lessons")
    serializer_class = CourseSerializer

    def get_permissions(self) -> list[BasePermission]:
        """Возвращает права для текущего action: модератор не может создавать и удалять курсы."""
        if self.action in ("create", "destroy"):
            self.permission_classes = [IsAuthenticated, ~IsModer]  # type: ignore[operator]
        else:
            self.permission_classes = [IsAuthenticated]
        return [permission() for permission in self.permission_classes]


class LessonCreateAPIView(generics.CreateAPIView):
    """Создание урока. Модератору недоступно."""

    serializer_class = LessonSerializer
    permission_classes = [IsAuthenticated, ~IsModer]  # type: ignore[operator]


class LessonListAPIView(generics.ListAPIView):
    """Список уроков."""

    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = [IsAuthenticated]


class LessonRetrieveAPIView(generics.RetrieveAPIView):
    """Просмотр одного урока."""

    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = [IsAuthenticated]


class LessonUpdateAPIView(generics.UpdateAPIView):
    """Редактирование урока."""

    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = [IsAuthenticated]


class LessonDestroyAPIView(generics.DestroyAPIView):
    """Удаление урока. Модератору недоступно."""

    queryset = Lesson.objects.all()
    permission_classes = [IsAuthenticated, ~IsModer]  # type: ignore[operator]
