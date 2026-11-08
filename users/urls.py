"""Маршруты приложения users."""

from django.urls import path
from rest_framework.routers import SimpleRouter

from users.views import (
    PaymentCreateAPIView,
    PaymentListAPIView,
    UserRegisterAPIView,
    UserTokenObtainPairView,
    UserTokenRefreshView,
    UserViewSet,
)

app_name = "users"

# SimpleRouter: у DefaultRouter корневая страница API заняла бы /users/ вместо списка пользователей
router = SimpleRouter()
router.register("", UserViewSet, basename="users")

# Конкретные пути идут до router.urls: иначе "payments" или "token" совпадут с шаблоном /users/<pk>/
urlpatterns = [
    path("register/", UserRegisterAPIView.as_view(), name="register"),
    path("token/", UserTokenObtainPairView.as_view(), name="token-obtain-pair"),
    path("token/refresh/", UserTokenRefreshView.as_view(), name="token-refresh"),
    path("payments/", PaymentListAPIView.as_view(), name="payment-list"),
    path("payments/create/", PaymentCreateAPIView.as_view(), name="payment-create"),
] + router.urls
