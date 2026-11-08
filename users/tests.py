"""Тесты приложения users: регистрация, JWT, профили, платежи и оплата через Stripe."""

from decimal import Decimal
from unittest import mock

import stripe
from django.test import SimpleTestCase, override_settings
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from lms.models import Course, Lesson
from users.models import CustomUser, Payment
from users.services import convert_to_cents, get_payment_status


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


def stripe_object(**fields: str) -> stripe.StripeObject:
    """Ответ Stripe с нужными полями: такой же объект, какой возвращает библиотека stripe."""
    return stripe.StripeObject.construct_from(fields, "sk_test_fake")


@override_settings(STRIPE_API_KEY="sk_test_fake", STRIPE_CURRENCY="rub")
class PaymentStripeTestCase(UsersTestCase):
    """Оплата курса через Stripe и проверка статуса. Stripe подменяется, запросы в сеть не уходят."""

    def setUp(self) -> None:
        """Задаёт цену курса и авторизует пользователя."""
        super().setUp()
        self.course.price = Decimal("15000.00")
        self.course.save()
        self.client.force_authenticate(self.user)
        self.url = reverse("users:payment-create")

    @mock.patch("stripe.checkout.Session.create")
    @mock.patch("stripe.Price.create")
    @mock.patch("stripe.Product.create")
    def test_payment_create(
        self, product_create: mock.Mock, price_create: mock.Mock, session_create: mock.Mock
    ) -> None:
        """Создаются продукт, цена и сессия в Stripe, ID и ссылка сохраняются в платеже."""
        product_create.return_value = stripe_object(id="prod_1")
        price_create.return_value = stripe_object(id="price_1")
        session_create.return_value = stripe_object(id="cs_1", url="https://checkout.stripe.com/c/pay/cs_1")

        response = self.client.post(self.url, {"course": self.course.pk})

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.json()["payment_url"], "https://checkout.stripe.com/c/pay/cs_1")

        payment = Payment.objects.get(pk=response.json()["id"])
        self.assertEqual(payment.user, self.user)
        self.assertEqual(payment.paid_course, self.course)
        self.assertEqual(payment.amount, Decimal("15000.00"))
        self.assertEqual(payment.payment_method, Payment.PaymentMethod.STRIPE)
        self.assertEqual(payment.status, Payment.Status.PENDING)
        self.assertEqual(
            (payment.stripe_product_id, payment.stripe_price_id, payment.stripe_session_id),
            ("prod_1", "price_1", "cs_1"),
        )

        self.assertEqual(product_create.call_args.kwargs["name"], self.course.title)
        self.assertEqual(
            price_create.call_args.kwargs, {"product": "prod_1", "unit_amount": 1500000, "currency": "rub"}
        )
        self.assertEqual(session_create.call_args.kwargs["line_items"], [{"price": "price_1", "quantity": 1}])
        self.assertEqual(session_create.call_args.kwargs["customer_email"], self.user.email)

    @mock.patch("stripe.Price.create", side_effect=stripe.InvalidRequestError("Invalid currency", param="currency"))
    @mock.patch("stripe.Product.create", return_value=stripe_object(id="prod_1"))
    def test_payment_create_stripe_error(self, product_create: mock.Mock, price_create: mock.Mock) -> None:
        """Ошибка Stripe возвращает 502, платёж не сохраняется."""
        response = self.client.post(self.url, {"course": self.course.pk})

        self.assertEqual(response.status_code, status.HTTP_502_BAD_GATEWAY)
        self.assertIn("Invalid currency", response.json()["detail"])
        self.assertFalse(Payment.objects.filter(payment_method=Payment.PaymentMethod.STRIPE).exists())

    @mock.patch("stripe.Product.create")
    def test_payment_create_without_price(self, product_create: mock.Mock) -> None:
        """Курс без цены оплатить нельзя, в Stripe запрос не уходит."""
        self.course.price = Decimal("0")
        self.course.save()
        response = self.client.post(self.url, {"course": self.course.pk})

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("course", response.json())
        product_create.assert_not_called()

    def test_payment_create_course_not_found(self) -> None:
        """Несуществующий курс возвращает ошибку."""
        response = self.client.post(self.url, {"course": 999})

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_payment_create_anonymous(self) -> None:
        """Аноним не может оплатить курс."""
        self.client.force_authenticate(None)
        response = self.client.post(self.url, {"course": self.course.pk})

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def create_stripe_payment(self, user: CustomUser) -> Payment:
        """Создаёт платёж через Stripe в статусе «Ожидает оплаты»."""
        payment: Payment = Payment.objects.create(
            user=user,
            paid_course=self.course,
            amount=self.course.price,
            payment_method=Payment.PaymentMethod.STRIPE,
            stripe_session_id="cs_1",
        )
        return payment

    @mock.patch("stripe.checkout.Session.retrieve")
    def test_payment_status_sync(self, session_retrieve: mock.Mock) -> None:
        """Статус сессии из Stripe сохраняется в платеже."""
        payment = self.create_stripe_payment(self.user)
        url = reverse("users:payment-status", args=(payment.pk,))
        cases = (
            (stripe_object(payment_status="unpaid", status="open"), Payment.Status.PENDING),
            (stripe_object(payment_status="paid", status="complete"), Payment.Status.PAID),
            (stripe_object(payment_status="unpaid", status="expired"), Payment.Status.EXPIRED),
        )
        for session, expected in cases:
            with self.subTest(expected=expected):
                session_retrieve.return_value = session
                response = self.client.get(url)

                self.assertEqual(response.status_code, status.HTTP_200_OK)
                self.assertEqual(response.json()["status"], expected)
                payment.refresh_from_db()
                self.assertEqual(payment.status, expected)
        session_retrieve.assert_called_with("cs_1")

    @mock.patch(
        "stripe.checkout.Session.retrieve", side_effect=stripe.InvalidRequestError("No such session", param="id")
    )
    def test_payment_status_stripe_error(self, session_retrieve: mock.Mock) -> None:
        """Ошибка Stripe при проверке статуса возвращает 502, статус не меняется."""
        payment = self.create_stripe_payment(self.user)
        response = self.client.get(reverse("users:payment-status", args=(payment.pk,)))

        self.assertEqual(response.status_code, status.HTTP_502_BAD_GATEWAY)
        payment.refresh_from_db()
        self.assertEqual(payment.status, Payment.Status.PENDING)

    @mock.patch("stripe.checkout.Session.retrieve")
    def test_payment_status_other_user(self, session_retrieve: mock.Mock) -> None:
        """Статус чужого платежа проверить нельзя."""
        payment = self.create_stripe_payment(self.other)
        response = self.client.get(reverse("users:payment-status", args=(payment.pk,)))

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        session_retrieve.assert_not_called()

    def test_payment_status_not_stripe(self) -> None:
        """Платёж наличными нельзя проверить через Stripe."""
        response = self.client.get(reverse("users:payment-status", args=(self.course_payment.pk,)))

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("detail", response.json())

    def test_payment_status_not_found(self) -> None:
        """Несуществующий платёж возвращает 404."""
        response = self.client.get(reverse("users:payment-status", args=(999,)))

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_payment_status_anonymous(self) -> None:
        """Аноним не может проверить статус."""
        payment = self.create_stripe_payment(self.user)
        self.client.force_authenticate(None)
        response = self.client.get(reverse("users:payment-status", args=(payment.pk,)))

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class ConvertToCentsTestCase(SimpleTestCase):
    """Перевод суммы в копейки для Stripe."""

    def test_convert_to_cents(self) -> None:
        """Сумма умножается на 100 без ошибок округления."""
        self.assertEqual(convert_to_cents(Decimal("15000.00")), 1500000)
        self.assertEqual(convert_to_cents(Decimal("199.99")), 19999)
        self.assertEqual(convert_to_cents(Decimal("0.10")), 10)


class PaymentStatusTestCase(SimpleTestCase):
    """Статус платежа по данным сессии оплаты из Stripe."""

    def test_get_payment_status(self) -> None:
        """Оплаченная сессия — «Оплачен», истёкшая — «Истёк», остальные — «Ожидает оплаты»."""
        self.assertEqual(get_payment_status({"payment_status": "paid", "status": "complete"}), Payment.Status.PAID)
        self.assertEqual(get_payment_status({"payment_status": "unpaid", "status": "expired"}), Payment.Status.EXPIRED)
        self.assertEqual(get_payment_status({"payment_status": "unpaid", "status": "open"}), Payment.Status.PENDING)
