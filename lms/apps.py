"""Конфигурация приложения lms."""

from django.apps import AppConfig


class LmsConfig(AppConfig):
    """Конфигурация приложения курсов и уроков."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "lms"
    verbose_name = "Курсы и уроки"
