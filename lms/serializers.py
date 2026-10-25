"""Сериализаторы приложения lms."""

from rest_framework import serializers

from lms.models import Course, Lesson


class LessonSerializer(serializers.ModelSerializer):
    """Сериализатор урока."""

    class Meta:
        """Мета-параметры сериализатора урока."""

        model = Lesson
        fields = "__all__"


class CourseSerializer(serializers.ModelSerializer):
    """Сериализатор курса с количеством уроков и списком уроков."""

    lessons_count = serializers.SerializerMethodField()
    lessons = LessonSerializer(many=True, read_only=True)

    class Meta:
        """Мета-параметры сериализатора курса."""

        model = Course
        fields = ("id", "title", "preview", "description", "lessons_count", "lessons")

    def get_lessons_count(self, obj: Course) -> int:
        """Возвращает количество уроков курса."""
        return int(obj.lessons.count())
