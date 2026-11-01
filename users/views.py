"""Контроллеры приложения users."""

from rest_framework import generics

from users.models import CustomUser
from users.serializers import UserProfileSerializer


class UserProfileAPIView(generics.RetrieveUpdateAPIView):
    """Просмотр и редактирование профиля любого пользователя."""

    queryset = CustomUser.objects.all()
    serializer_class = UserProfileSerializer
