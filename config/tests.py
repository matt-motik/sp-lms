"""Тесты документации API."""

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase


class DocumentationTestCase(APITestCase):
    """Документация доступна без авторизации и описывает все эндпоинты."""

    def test_docs_available(self) -> None:
        """Схема, Swagger и Redoc открываются без токена."""
        for name in ("schema", "swagger-ui", "redoc"):
            with self.subTest(name=name):
                self.assertEqual(self.client.get(reverse(name)).status_code, status.HTTP_200_OK)

    def test_schema_paths(self) -> None:
        """В схеме есть все эндпоинты проекта."""
        response = self.client.get(reverse("schema"), {"format": "json"})
        paths = response.json()["paths"]

        expected = (
            "/courses/",
            "/courses/{id}/",
            "/lessons/",
            "/lessons/create/",
            "/lessons/{id}/",
            "/lessons/{id}/update/",
            "/lessons/{id}/delete/",
            "/subscriptions/",
            "/users/",
            "/users/{id}/",
            "/users/register/",
            "/users/token/",
            "/users/token/refresh/",
            "/users/payments/",
            "/users/payments/create/",
            "/users/payments/{id}/status/",
        )
        for path in expected:
            with self.subTest(path=path):
                self.assertIn(path, paths)
