"""Сервисные функции для работы с платёжным сервисом Stripe."""

from collections.abc import Iterator
from contextlib import contextmanager
from decimal import Decimal
from typing import Any

import stripe
from django.conf import settings
from rest_framework import status
from rest_framework.exceptions import APIException

from lms.models import Course
from users.models import Payment


class StripeServiceError(APIException):
    """Ошибка платёжного сервиса: Stripe недоступен или отклонил запрос."""

    status_code = status.HTTP_502_BAD_GATEWAY
    default_detail = "Платёжный сервис временно недоступен."
    default_code = "stripe_error"


@contextmanager
def handle_stripe_errors(action: str) -> Iterator[None]:
    """Подставляет ключ API и превращает ошибки Stripe в ответ API с понятным текстом."""
    stripe.api_key = settings.STRIPE_API_KEY
    try:
        yield
    except stripe.StripeError as error:
        raise StripeServiceError(f"Не удалось {action}: {error.user_message or error}") from error


def convert_to_cents(amount: Decimal) -> int:
    """Переводит сумму в копейки: Stripe принимает цену в минимальных единицах валюты."""
    return int((amount * 100).quantize(Decimal("1")))


def create_stripe_product(course: Course) -> dict[str, Any]:
    """Создаёт продукт в Stripe для курса и возвращает ответ Stripe."""
    with handle_stripe_errors("создать продукт в Stripe"):
        product = stripe.Product.create(name=course.title, metadata={"course_id": str(course.pk)})
    response: dict[str, Any] = product.to_dict()
    return response


def create_stripe_price(product_id: str, amount: Decimal) -> dict[str, Any]:
    """Создаёт цену продукта в Stripe и возвращает ответ Stripe. Сумма передаётся в копейках."""
    with handle_stripe_errors("создать цену в Stripe"):
        price = stripe.Price.create(
            product=product_id,
            unit_amount=convert_to_cents(amount),
            currency=settings.STRIPE_CURRENCY,
        )
    response: dict[str, Any] = price.to_dict()
    return response


def create_stripe_session(price_id: str, payment: Payment) -> dict[str, Any]:
    """Создаёт сессию оплаты в Stripe и возвращает ответ Stripe со ссылкой на оплату в поле url."""
    with handle_stripe_errors("создать сессию оплаты в Stripe"):
        session = stripe.checkout.Session.create(
            mode="payment",
            line_items=[{"price": price_id, "quantity": 1}],
            success_url=settings.STRIPE_SUCCESS_URL,
            cancel_url=settings.STRIPE_CANCEL_URL,
            customer_email=payment.user.email,
            client_reference_id=str(payment.pk),
            metadata={"payment_id": str(payment.pk)},
        )
    response: dict[str, Any] = session.to_dict()
    return response


def retrieve_stripe_session(session_id: str) -> dict[str, Any]:
    """Получает сессию оплаты из Stripe и возвращает ответ Stripe."""
    with handle_stripe_errors("получить сессию оплаты из Stripe"):
        session = stripe.checkout.Session.retrieve(session_id)
    response: dict[str, Any] = session.to_dict()
    return response


def get_payment_status(session: dict[str, Any]) -> str:
    """Возвращает статус платежа по данным сессии оплаты из Stripe."""
    if session.get("payment_status") == "paid":
        return str(Payment.Status.PAID)
    if session.get("status") == "expired":
        return str(Payment.Status.EXPIRED)
    return str(Payment.Status.PENDING)
