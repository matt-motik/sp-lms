"""Админка приложения users."""

from django.contrib import admin

from users.models import CustomUser


@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    """Настройки админки для пользователей."""

    list_display = ("id", "email", "phone", "city", "is_staff", "is_active")
    search_fields = ("email", "phone", "city")
