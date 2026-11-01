"""Админка приложения lms."""

from django.contrib import admin

from lms.models import Course, Lesson


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    """Настройки админки для курсов."""

    list_display = ("id", "title")
    search_fields = ("title",)


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    """Настройки админки для уроков."""

    list_display = ("id", "title", "course")
    list_filter = ("course",)
    search_fields = ("title",)
