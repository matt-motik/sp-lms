"""Отложенные задачи приложения lms."""

from celery import shared_task
from django.conf import settings
from django.core.mail import send_mass_mail

from lms.models import Course


@shared_task
def send_course_update(course_id: int) -> None:
    """Отправляет подписчикам курса письмо об обновлении материалов."""
    course = Course.objects.get(pk=course_id)
    emails = course.subscriptions.values_list("user__email", flat=True)

    subject = f"Обновление курса «{course.title}»"
    message = f"Материалы курса «{course.title}», на который вы подписаны, обновлены."
    # Каждому подписчику отдельное письмо, чтобы получатели не видели адреса друг друга
    send_mass_mail(
        [(subject, message, settings.DEFAULT_FROM_EMAIL, [email]) for email in emails],
        fail_silently=False,
    )
