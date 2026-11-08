# Модуль: `users/services.py`

*Сгенерировано: 2026-11-08 19:33:44*

---

<div id="StripeServiceError"></div>

## StripeServiceError

**Тип:** class

**Кратко:** Ошибка платёжного сервиса: Stripe недоступен или отклонил запрос.

### Полная документация

```text
Ошибка платёжного сервиса: Stripe недоступен или отклонил запрос.
```

---

<div id="handle_stripe_errors"></div>

## handle_stripe_errors

**Тип:** function

**Кратко:** Подставляет ключ API и превращает ошибки Stripe в ответ API с понятным текстом.

### Полная документация

```text
Подставляет ключ API и превращает ошибки Stripe в ответ API с понятным текстом.
```

---

<div id="convert_to_cents"></div>

## convert_to_cents

**Тип:** function

**Кратко:** Переводит сумму в копейки: Stripe принимает цену в минимальных единицах валюты.

### Полная документация

```text
Переводит сумму в копейки: Stripe принимает цену в минимальных единицах валюты.
```

---

<div id="create_stripe_product"></div>

## create_stripe_product

**Тип:** function

**Кратко:** Создаёт продукт в Stripe для курса и возвращает ответ Stripe.

### Полная документация

```text
Создаёт продукт в Stripe для курса и возвращает ответ Stripe.
```

---

<div id="create_stripe_price"></div>

## create_stripe_price

**Тип:** function

**Кратко:** Создаёт цену продукта в Stripe и возвращает ответ Stripe. Сумма передаётся в копейках.

### Полная документация

```text
Создаёт цену продукта в Stripe и возвращает ответ Stripe. Сумма передаётся в копейках.
```

---

<div id="create_stripe_session"></div>

## create_stripe_session

**Тип:** function

**Кратко:** Создаёт сессию оплаты в Stripe и возвращает ответ Stripe со ссылкой на оплату в поле url.

### Полная документация

```text
Создаёт сессию оплаты в Stripe и возвращает ответ Stripe со ссылкой на оплату в поле url.
```

---

<div id="retrieve_stripe_session"></div>

## retrieve_stripe_session

**Тип:** function

**Кратко:** Получает сессию оплаты из Stripe и возвращает ответ Stripe.

### Полная документация

```text
Получает сессию оплаты из Stripe и возвращает ответ Stripe.
```

---

<div id="get_payment_status"></div>

## get_payment_status

**Тип:** function

**Кратко:** Возвращает статус платежа по данным сессии оплаты из Stripe.

### Полная документация

```text
Возвращает статус платежа по данным сессии оплаты из Stripe.
```

---
