# Модуль: `users/serializers.py`

*Сгенерировано: 2026-11-08 19:17:59*

---

<div id="PaymentSerializer"></div>

## PaymentSerializer

**Тип:** class

**Кратко:** Сериализатор платежа.

### Полная документация

```text
Сериализатор платежа.
```

---

<div id="PaymentSerializer-Meta"></div>

## PaymentSerializer.Meta

**Тип:** class

**Кратко:** Мета-параметры сериализатора платежа.

### Полная документация

```text
Мета-параметры сериализатора платежа.
```

---

<div id="PaymentCreateSerializer"></div>

## PaymentCreateSerializer

**Тип:** class

**Кратко:** Сериализатор запроса на оплату курса: принимает ID курса.

### Полная документация

```text
Сериализатор запроса на оплату курса: принимает ID курса.
```

---

<div id="PaymentCreateSerializer-validate_course"></div>

## PaymentCreateSerializer.validate_course

**Тип:** method

**Кратко:** Проверяет, что у курса указана цена.

### Полная документация

```text
Проверяет, что у курса указана цена.
```

---

<div id="PaymentStripeSerializer"></div>

## PaymentStripeSerializer

**Тип:** class

**Кратко:** Сериализатор платежа через Stripe: данные платежа и ссылка на оплату.

### Полная документация

```text
Сериализатор платежа через Stripe: данные платежа и ссылка на оплату.
```

---

<div id="PaymentStripeSerializer-Meta"></div>

## PaymentStripeSerializer.Meta

**Тип:** class

**Кратко:** Мета-параметры сериализатора платежа через Stripe.

### Полная документация

```text
Мета-параметры сериализатора платежа через Stripe.
```

---

<div id="PaymentHistorySerializer"></div>

## PaymentHistorySerializer

**Тип:** class

**Кратко:** Сериализатор платежа для истории в профиле: с названиями курса, урока, способа и статуса оплаты.

### Полная документация

```text
Сериализатор платежа для истории в профиле: с названиями курса, урока, способа и статуса оплаты.
```

---

<div id="PaymentHistorySerializer-Meta"></div>

## PaymentHistorySerializer.Meta

**Тип:** class

**Кратко:** Мета-параметры сериализатора истории платежей.

### Полная документация

```text
Мета-параметры сериализатора истории платежей.
```

---

<div id="UserProfileSerializer"></div>

## UserProfileSerializer

**Тип:** class

**Кратко:** Сериализатор профиля пользователя с историей платежей.

### Полная документация

```text
Сериализатор профиля пользователя с историей платежей.
```

---

<div id="UserProfileSerializer-Meta"></div>

## UserProfileSerializer.Meta

**Тип:** class

**Кратко:** Мета-параметры сериализатора профиля.

### Полная документация

```text
Мета-параметры сериализатора профиля.
```

---

<div id="UserPublicSerializer"></div>

## UserPublicSerializer

**Тип:** class

**Кратко:** Сериализатор чужого профиля: только общая информация, без фамилии, пароля и платежей.

### Полная документация

```text
Сериализатор чужого профиля: только общая информация, без фамилии, пароля и платежей.
```

---

<div id="UserPublicSerializer-Meta"></div>

## UserPublicSerializer.Meta

**Тип:** class

**Кратко:** Мета-параметры публичного сериализатора профиля.

### Полная документация

```text
Мета-параметры публичного сериализатора профиля.
```

---

<div id="UserRegisterSerializer"></div>

## UserRegisterSerializer

**Тип:** class

**Кратко:** Сериализатор регистрации пользователя.

### Полная документация

```text
Сериализатор регистрации пользователя.
```

---

<div id="UserRegisterSerializer-Meta"></div>

## UserRegisterSerializer.Meta

**Тип:** class

**Кратко:** Мета-параметры сериализатора регистрации.

### Полная документация

```text
Мета-параметры сериализатора регистрации.
```

---

<div id="UserRegisterSerializer-validate_email"></div>

## UserRegisterSerializer.validate_email

**Тип:** method

**Кратко:** Проверяет, что пользователь с таким email ещё не зарегистрирован.

### Полная документация

```text
Проверяет, что пользователь с таким email ещё не зарегистрирован.
```

---

<div id="UserRegisterSerializer-validate"></div>

## UserRegisterSerializer.validate

**Тип:** method

**Кратко:** Проверяет пароль стандартными валидаторами Django.

### Полная документация

```text
Проверяет пароль стандартными валидаторами Django.
```

---

<div id="UserRegisterSerializer-create"></div>

## UserRegisterSerializer.create

**Тип:** method

**Кратко:** Создаёт пользователя с хешированным паролем.

### Полная документация

```text
Создаёт пользователя с хешированным паролем.
```

---
