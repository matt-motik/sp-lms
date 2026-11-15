"""Тесты приложения users: регистрация, JWT, профили и платежи."""

from decimal import Decimal

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from lms.models import Course, Lesson
from users.models import CustomUser, Payment


class UsersTestCase(APITestCase):
    """Общие тестовые данные: два пользователя и платежи первого."""

    def setUp(self) -> None:
        """Создаёт пользователей, курс, урок и платежи."""
        self.user = CustomUser.objects.create_user(
            email="user@test.ru", password="pass12345", first_name="Иван", last_name="Иванов"
        )
        self.other = CustomUser.objects.create_user(email="other@test.ru", password="pass12345")

        self.course = Course.objects.create(title="Python", owner=self.user)
        self.lesson = Lesson.objects.create(course=self.course, title="Переменные", owner=self.user)
        self.course_payment = Payment.objects.create(
            user=self.user,
            paid_course=self.course,
            amount=Decimal("10000.00"),
            payment_method=Payment.PaymentMethod.TRANSFER,
        )
        self.lesson_payment = Payment.objects.create(
            user=self.user,
            paid_lesson=self.lesson,
            amount=Decimal("1000.00"),
            payment_method=Payment.PaymentMethod.CASH,
        )


class RegisterTestCase(UsersTestCase):
    """Регистрация пользователя."""

    def test_register(self) -> None:
        """Регистрация доступна без авторизации, пароль хешируется."""
        data = {"email": "new@test.ru", "password": "Strong-pass-42"}
        response = self.client.post(reverse("users:register"), data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertNotIn("password", response.json())
        self.assertTrue(CustomUser.objects.get(email="new@test.ru").check_password("Strong-pass-42"))

    def test_register_existing_email(self) -> None:
        """Нельзя зарегистрироваться с уже занятым email."""
        data = {"email": "USER@test.ru", "password": "Strong-pass-42"}
        response = self.client.post(reverse("users:register"), data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("email", response.json())

    def test_register_weak_password(self) -> None:
        """Слабый пароль не проходит валидацию."""
        data = {"email": "new@test.ru", "password": "123"}
        response = self.client.post(reverse("users:register"), data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("password", response.json())
        self.assertFalse(CustomUser.objects.filter(email="new@test.ru").exists())


class TokenTestCase(UsersTestCase):
    """Получение и обновление JWT."""

    def test_token_obtain_and_refresh(self) -> None:
        """По email и паролю выдаётся пара токенов, refresh-токен обновляет access."""
        response = self.client.post(
            reverse("users:token-obtain-pair"), {"email": "user@test.ru", "password": "pass12345"}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.json())

        response = self.client.post(reverse("users:token-refresh"), {"refresh": response.json()["refresh"]})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.json())

    def test_token_wrong_password(self) -> None:
        """С неверным паролем токен не выдаётся."""
        response = self.client.post(reverse("users:token-obtain-pair"), {"email": "user@test.ru", "password": "wrong"})

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_access_with_token(self) -> None:
        """С access-токеном в заголовке запрос проходит авторизацию."""
        response = self.client.post(
            reverse("users:token-obtain-pair"), {"email": "user@test.ru", "password": "pass12345"}
        )
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {response.json()['access']}")

        self.assertEqual(self.client.get(reverse("users:users-list")).status_code, status.HTTP_200_OK)


class UserProfileTestCase(UsersTestCase):
    """Просмотр, редактирование и удаление профилей."""

    def test_users_list(self) -> None:
        """Список пользователей отдаёт только общую информацию."""
        self.client.force_authenticate(self.user)
        response = self.client.get(reverse("users:users-list"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.json()), 2)
        self.assertNotIn("last_name", response.json()[0])
        self.assertNotIn("payments", response.json()[0])

    def test_users_list_anonymous(self) -> None:
        """Аноним не видит список пользователей."""
        response = self.client.get(reverse("users:users-list"))

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_own_profile(self) -> None:
        """Свой профиль отдаётся полностью, с фамилией и историей платежей."""
        self.client.force_authenticate(self.user)
        response = self.client.get(reverse("users:users-detail", args=(self.user.pk,)))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()["last_name"], "Иванов")
        self.assertEqual(len(response.json()["payments"]), 2)
        self.assertNotIn("password", response.json())

    def test_other_profile(self) -> None:
        """Чужой профиль отдаётся без фамилии и платежей."""
        self.client.force_authenticate(self.other)
        response = self.client.get(reverse("users:users-detail", args=(self.user.pk,)))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()["first_name"], "Иван")
        self.assertNotIn("last_name", response.json())
        self.assertNotIn("payments", response.json())

    def test_update_own_profile(self) -> None:
        """Пользователь редактирует свой профиль."""
        self.client.force_authenticate(self.user)
        response = self.client.patch(reverse("users:users-detail", args=(self.user.pk,)), {"city": "Москва"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertEqual(self.user.city, "Москва")

    def test_update_other_profile_forbidden(self) -> None:
        """Чужой профиль редактировать нельзя."""
        self.client.force_authenticate(self.other)
        response = self.client.patch(reverse("users:users-detail", args=(self.user.pk,)), {"city": "Москва"})

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.user.refresh_from_db()
        self.assertEqual(self.user.city, "")

    def test_delete_other_profile_forbidden(self) -> None:
        """Чужой профиль удалить нельзя."""
        self.client.force_authenticate(self.other)
        response = self.client.delete(reverse("users:users-detail", args=(self.user.pk,)))

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(CustomUser.objects.filter(pk=self.user.pk).exists())

    def test_delete_own_profile(self) -> None:
        """Пользователь удаляет свой профиль."""
        self.client.force_authenticate(self.other)
        response = self.client.delete(reverse("users:users-detail", args=(self.other.pk,)))

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(CustomUser.objects.filter(pk=self.other.pk).exists())


class PaymentTestCase(UsersTestCase):
    """Список платежей с фильтрацией и сортировкой."""

    def setUp(self) -> None:
        """Авторизует пользователя."""
        super().setUp()
        self.client.force_authenticate(self.user)
        self.url = reverse("users:payment-list")

    def test_payment_list(self) -> None:
        """Список платежей отдаётся авторизованному пользователю."""
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.json()), 2)

    def test_payment_filter(self) -> None:
        """Платежи фильтруются по курсу, уроку и способу оплаты."""
        response = self.client.get(self.url, {"paid_course": self.course.pk})
        self.assertEqual([item["id"] for item in response.json()], [self.course_payment.pk])

        response = self.client.get(self.url, {"paid_lesson": self.lesson.pk})
        self.assertEqual([item["id"] for item in response.json()], [self.lesson_payment.pk])

        response = self.client.get(self.url, {"payment_method": Payment.PaymentMethod.CASH})
        self.assertEqual([item["id"] for item in response.json()], [self.lesson_payment.pk])

    def test_payment_ordering(self) -> None:
        """Платежи сортируются по дате оплаты."""
        response = self.client.get(self.url, {"ordering": "payment_date"})
        self.assertEqual([item["id"] for item in response.json()], [self.course_payment.pk, self.lesson_payment.pk])

        response = self.client.get(self.url, {"ordering": "-payment_date"})
        self.assertEqual([item["id"] for item in response.json()], [self.lesson_payment.pk, self.course_payment.pk])

    def test_payment_list_anonymous(self) -> None:
        """Аноним не видит платежи."""
        self.client.force_authenticate(None)
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
