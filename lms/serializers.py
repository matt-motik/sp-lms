"""Сериализаторы приложения lms."""

from rest_framework import serializers

from lms.models import Course, Lesson
from lms.validators import YoutubeLinkValidator


class LessonSerializer(serializers.ModelSerializer):
    """Сериализатор урока."""

    class Meta:
        """Мета-параметры сериализатора урока."""

        model = Lesson
        fields = "__all__"
        read_only_fields = ("owner",)
        validators = [YoutubeLinkValidator(field="video_url"), YoutubeLinkValidator(field="description")]


class CourseSerializer(serializers.ModelSerializer):
    """Сериализатор курса с количеством уроков и списком уроков."""

    lessons_count = serializers.SerializerMethodField()
    lessons = LessonSerializer(many=True, read_only=True)

    class Meta:
        """Мета-параметры сериализатора курса."""

        model = Course
        fields = ("id", "title", "preview", "description", "owner", "lessons_count", "lessons")
        read_only_fields = ("owner",)
        validators = [YoutubeLinkValidator(field="description")]

    def get_lessons_count(self, obj: Course) -> int:
        """Возвращает количество уроков курса."""
        return int(obj.lessons.count())
