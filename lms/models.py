"""Модели приложения lms."""

from django.conf import settings
from django.db import models


class Course(models.Model):
    """Модель курса."""

    title = models.CharField(max_length=255, verbose_name="Название")
    preview = models.ImageField(upload_to="lms/courses/", blank=True, null=True, verbose_name="Превью")
    description = models.TextField(blank=True, verbose_name="Описание")
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="courses",
        verbose_name="Владелец",
    )

    class Meta:
        """Мета-параметры модели Course."""

        verbose_name = "Курс"
        verbose_name_plural = "Курсы"
        ordering = ("id",)

    def __str__(self) -> str:
        """Возвращает название курса."""
        return str(self.title)


class Lesson(models.Model):
    """Модель урока."""

    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="lessons", verbose_name="Курс")
    title = models.CharField(max_length=255, verbose_name="Название")
    description = models.TextField(blank=True, verbose_name="Описание")
    preview = models.ImageField(upload_to="lms/lessons/", blank=True, null=True, verbose_name="Превью")
    video_url = models.URLField(blank=True, verbose_name="Ссылка на видео")
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="lessons",
        verbose_name="Владелец",
    )

    class Meta:
        """Мета-параметры модели Lesson."""

        verbose_name = "Урок"
        verbose_name_plural = "Уроки"
        ordering = ("id",)

    def __str__(self) -> str:
        """Возвращает название урока."""
        return str(self.title)


class Subscription(models.Model):
    """Модель подписки пользователя на обновления курса."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="subscriptions",
        verbose_name="Пользователь",
    )
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="subscriptions", verbose_name="Курс")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата подписки")

    class Meta:
        """Мета-параметры модели Subscription."""

        verbose_name = "Подписка"
        verbose_name_plural = "Подписки"
        constraints = [
            models.UniqueConstraint(fields=("user", "course"), name="unique_user_course_subscription"),
        ]

    def __str__(self) -> str:
        """Возвращает пользователя и курс подписки."""
        return f"{self.user} — {self.course}"
