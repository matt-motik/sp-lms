"""Маршруты приложения users."""

from django.urls import path

from users.views import UserProfileAPIView

app_name = "users"

urlpatterns = [
    path("<int:pk>/", UserProfileAPIView.as_view(), name="user-profile"),
]
