"""Сериализаторы приложения lms."""

from rest_framework import serializers

from lms.models import Course, Lesson


class CourseSerializer(serializers.ModelSerializer):
    """Сериализатор курса."""

    class Meta:
        """Мета-параметры сериализатора курса."""

        model = Course
        fields = "__all__"


class LessonSerializer(serializers.ModelSerializer):
    """Сериализатор урока."""

    class Meta:
        """Мета-параметры сериализатора урока."""

        model = Lesson
        fields = "__all__"
