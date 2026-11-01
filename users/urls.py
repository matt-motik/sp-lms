"""Маршруты приложения users."""

from django.urls import path
from rest_framework.permissions import AllowAny
from rest_framework.routers import SimpleRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from users.views import PaymentListAPIView, UserRegisterAPIView, UserViewSet

app_name = "users"

# SimpleRouter: у DefaultRouter корневая страница API заняла бы /users/ вместо списка пользователей
router = SimpleRouter()
router.register("", UserViewSet, basename="users")

# Конкретные пути идут до router.urls: иначе "payments" или "token" совпадут с шаблоном /users/<pk>/
urlpatterns = [
    path("register/", UserRegisterAPIView.as_view(), name="register"),
    path("token/", TokenObtainPairView.as_view(permission_classes=(AllowAny,)), name="token-obtain-pair"),
    path("token/refresh/", TokenRefreshView.as_view(permission_classes=(AllowAny,)), name="token-refresh"),
    path("payments/", PaymentListAPIView.as_view(), name="payment-list"),
] + router.urls
