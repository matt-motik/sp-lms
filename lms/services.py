"""Сервисные функции приложения lms."""

from datetime import datetime, timedelta

from django.utils import timezone

from lms.models import Course
from lms.tasks import send_course_update

# Подписчики получают письмо, только если курс не обновлялся дольше этого интервала
UPDATE_NOTIFY_INTERVAL = timedelta(hours=4)


def is_notify_needed(updated_at: datetime) -> bool:
    """Возвращает True, если с прошлого обновления курса прошло больше UPDATE_NOTIFY_INTERVAL."""
    return bool(timezone.now() - updated_at > UPDATE_NOTIFY_INTERVAL)


def notify_subscribers(course: Course, last_updated_at: datetime) -> None:
    """Ставит в очередь рассылку подписчикам, если курс долго не обновлялся."""
    if is_notify_needed(last_updated_at):
        send_course_update.delay(course.pk)
