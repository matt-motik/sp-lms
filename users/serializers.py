"""Сериализаторы приложения users."""

from rest_framework import serializers

from users.models import CustomUser


class UserProfileSerializer(serializers.ModelSerializer):
    """Сериализатор профиля пользователя."""

    class Meta:
        """Мета-параметры сериализатора профиля."""

        model = CustomUser
        fields = ("id", "email", "first_name", "last_name", "phone", "city", "avatar")
