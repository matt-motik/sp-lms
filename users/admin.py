"""Админка приложения users."""

from django.contrib import admin

from users.models import CustomUser, Payment


@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    """Настройки админки для пользователей."""

    list_display = ("id", "email", "phone", "city", "is_staff", "is_active")
    search_fields = ("email", "phone", "city")


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    """Настройки админки для платежей."""

    list_display = ("id", "user", "payment_date", "paid_course", "paid_lesson", "amount", "payment_method")
    list_filter = ("payment_method", "paid_course")
    search_fields = ("user__email",)
