"""Менеджер модели пользователя."""

from typing import TYPE_CHECKING, Any

from django.contrib.auth.base_user import BaseUserManager

if TYPE_CHECKING:
    from users.models import CustomUser


class CustomUserManager(BaseUserManager):
    """Менеджер пользователей, использующий email вместо username."""

    use_in_migrations = True

    def create_user(self, email: str, password: str | None = None, **extra_fields: Any) -> CustomUser:
        """Создаёт и сохраняет обычного пользователя."""
        if not email:
            raise ValueError("Email обязателен")
        email = self.normalize_email(email)
        user: CustomUser = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email: str, password: str | None = None, **extra_fields: Any) -> CustomUser:
        """Создаёт и сохраняет суперпользователя."""
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("У суперпользователя должно быть is_staff=True")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("У суперпользователя должно быть is_superuser=True")

        return self.create_user(email, password, **extra_fields)
