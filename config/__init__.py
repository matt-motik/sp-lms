"""Настройки проекта sp-lms."""

from .celery import app as celery_app

__all__ = ("celery_app",)
