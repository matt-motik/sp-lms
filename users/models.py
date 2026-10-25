"""Модели приложения users."""

from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone

from users.managers import CustomUserManager


class CustomUser(AbstractUser):
    """Кастомная модель пользователя с авторизацией по email."""

    username = None
    email = models.EmailField(unique=True, verbose_name="Email")
    phone = models.CharField(max_length=35, blank=True, verbose_name="Телефон")
    city = models.CharField(max_length=100, blank=True, verbose_name="Город")
    avatar = models.ImageField(upload_to="users/avatars/", blank=True, null=True, verbose_name="Аватар")

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS: list[str] = []

    objects = CustomUserManager()

    class Meta:
        """Мета-параметры модели CustomUser."""

        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"

    def __str__(self) -> str:
        """Возвращает email пользователя."""
        return str(self.email)


class Payment(models.Model):
    """Модель платежа за курс или отдельный урок."""

    class PaymentMethod(models.TextChoices):
        """Способы оплаты."""

        CASH = "cash", "Наличные"
        TRANSFER = "transfer", "Перевод на счёт"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="payments",
        verbose_name="Пользователь",
    )
    payment_date = models.DateTimeField(default=timezone.now, verbose_name="Дата оплаты")
    paid_course = models.ForeignKey(
        "lms.Course",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="payments",
        verbose_name="Оплаченный курс",
    )
    paid_lesson = models.ForeignKey(
        "lms.Lesson",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="payments",
        verbose_name="Оплаченный урок",
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Сумма оплаты")
    payment_method = models.CharField(
        max_length=20,
        choices=PaymentMethod.choices,
        verbose_name="Способ оплаты",
    )

    class Meta:
        """Мета-параметры модели Payment."""

        verbose_name = "Платёж"
        verbose_name_plural = "Платежи"
        ordering = ("-payment_date",)

    def __str__(self) -> str:
        """Возвращает краткое описание платежа."""
        return f"{self.user} — {self.amount} ({self.get_payment_method_display()})"
