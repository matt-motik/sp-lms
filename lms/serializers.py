"""Сериализаторы приложения lms."""

from rest_framework import serializers

from lms.models import Course, Lesson, Subscription
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
    """Сериализатор курса с количеством уроков, списком уроков и признаком подписки."""

    lessons_count = serializers.SerializerMethodField()
    lessons = LessonSerializer(many=True, read_only=True)
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        """Мета-параметры сериализатора курса."""

        model = Course
        fields = ("id", "title", "preview", "description", "owner", "lessons_count", "lessons", "is_subscribed")
        read_only_fields = ("owner",)
        validators = [YoutubeLinkValidator(field="description")]

    def get_lessons_count(self, obj: Course) -> int:
        """Возвращает количество уроков курса."""
        return int(obj.lessons.count())

    def get_is_subscribed(self, obj: Course) -> bool:
        """Возвращает True, если текущий пользователь подписан на обновления курса."""
        request = self.context.get("request")
        if request is None or not request.user.is_authenticated:
            return False
        return bool(obj.subscriptions.filter(user=request.user).exists())


class SubscriptionSerializer(serializers.ModelSerializer):
    """Сериализатор подписки: принимает ID курса."""

    class Meta:
        """Мета-параметры сериализатора подписки."""

        model = Subscription
        fields = ("course",)
