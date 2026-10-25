"""Модели приложения lms."""

from django.db import models


class Course(models.Model):
    """Модель курса."""

    title = models.CharField(max_length=255, verbose_name="Название")
    preview = models.ImageField(upload_to="lms/courses/", blank=True, null=True, verbose_name="Превью")
    description = models.TextField(blank=True, verbose_name="Описание")

    class Meta:
        """Мета-параметры модели Course."""

        verbose_name = "Курс"
        verbose_name_plural = "Курсы"

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

    class Meta:
        """Мета-параметры модели Lesson."""

        verbose_name = "Урок"
        verbose_name_plural = "Уроки"

    def __str__(self) -> str:
        """Возвращает название урока."""
        return str(self.title)
