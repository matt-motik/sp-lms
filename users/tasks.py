"""Периодические задачи приложения users."""

from datetime import timedelta

from celery import shared_task
from django.utils import timezone

from users.models import CustomUser

# Пользователь блокируется, если не заходил дольше этого срока
INACTIVE_PERIOD = timedelta(days=30)


@shared_task
def block_inactive_users() -> int:
    """Блокирует пользователей, которые не заходили дольше INACTIVE_PERIOD. Возвращает число заблокированных."""
    # Пользователи без last_login (ни разу не входили) под условие last_login__lt не попадают
    inactive_users = CustomUser.objects.filter(
        is_active=True,
        is_superuser=False,
        is_staff=False,
        last_login__lt=timezone.now() - INACTIVE_PERIOD,
    )
    return int(inactive_users.update(is_active=False))
