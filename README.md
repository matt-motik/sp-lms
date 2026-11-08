# SkyPro Модуль DRF. Учебный проект: LMS-система на Django REST framework

[![Python](https://img.shields.io/badge/Python-3.14+-blue.svg)](https://www.python.org/)
[![Django](https://img.shields.io/badge/Django-6.1+-green.svg)](https://www.djangoproject.com/)
[![DRF](https://img.shields.io/badge/DRF-3.18+-red.svg)](https://www.django-rest-framework.org/)
[![Ruff](https://img.shields.io/badge/Ruff-0.17+-purple.svg)](https://docs.astral.sh/ruff/)

Бэкенд LMS-системы, в которой можно размещать курсы и уроки. Сервер возвращает клиенту JSON-структуры и рассчитан на работу с SPA-приложением.

## 🚀 Возможности программы

- **Кастомный пользователь** `CustomUser` с авторизацией по email, полями телефон, город, аватар
- **CRUD курсов** на основе `ModelViewSet` и `DefaultRouter`
- **CRUD уроков** на основе Generic-классов (`ListAPIView`, `RetrieveAPIView`, `CreateAPIView`, `UpdateAPIView`, `DestroyAPIView`)
- **Связь курс → уроки**: в одном курсе много уроков, при удалении курса удаляются его уроки
- **Редактирование профиля любого пользователя** через `RetrieveUpdateAPIView` (доп. задание)
- **Загрузка изображений**: превью курсов и уроков, аватары пользователей (`MEDIA_ROOT`)
- **Количество и список уроков в курсе**: `lessons_count` через `SerializerMethodField` и вложенный `LessonSerializer`
- **Платежи** `Payment`: пользователь, дата, оплаченный курс или урок, сумма, способ оплаты (наличные / перевод)
- **Фильтрация платежей** по курсу, уроку и способу оплаты, сортировка по дате (`django-filter`, `OrderingFilter`)
- **История платежей в профиле** пользователя с названиями курсов и уроков
- **Фикстуры** с курсами, уроками, пользователями и платежами
- **Коллекция Postman** для проверки всех эндпоинтов
- **JWT-авторизация** (`djangorestframework-simplejwt`): все эндпоинты закрыты, открыты только регистрация и получение токенов
- **Регистрация и CRUD пользователей** с проверкой занятого email и валидацией пароля
- **Группа модераторов**: просмотр и редактирование любых курсов и уроков без права создавать и удалять
- **Владельцы курсов и уроков**: владелец назначается автоматически, обычный пользователь видит и меняет только своё
- **Профили**: чужой профиль только с общей информацией, редактировать и удалять можно только свой
- **Валидация ссылок**: в материалах курсов и уроков допускаются только ссылки на youtube.com (`lms/validators.py`)
- **Подписка на обновления курса**: модель `Subscription`, эндпоинт подписки/отписки, признак `is_subscribed` в курсе
- **Пагинация** списков курсов и уроков (`lms/paginators.py`)
- **Тесты** на все эндпоинты проекта (`APITestCase`), отчёт покрытия в `coverage.txt`
- **Админ-панель** для курсов, уроков, подписок, пользователей и платежей

## 📋 Содержание

- [Технологии](#технологии)
- [Установка](#установка)
- [Конфигурация](#конфигурация)
- [Использование](#использование)
- [Разработка](#разработка)
  - [Структура проекта](#структура-проекта)
  - [Линтеры и форматирование](#линтеры)
- [To do](#to-do)
- [Команда проекта](#команда-проекта)

<div id="технологии"></div>

## Технологии

| Компонент | Технология |
|-----------|------------|
| **Язык** | Python 3.14 |
| **Фреймворк** | Django 6.1 |
| **API** | Django REST framework 3.18 |
| **Фильтрация** | django-filter |
| **Авторизация** | Simple JWT |
| **База данных** | PostgreSQL |
| **Изображения** | Pillow |
| **Управление зависимостями** | uv |
| **Линтинг** | Ruff |
| **Типизация** | MyPy |
| **Pre-commit** | pre-commit |
| **Тестирование API** | Postman |

<div id="установка"></div>

## Установка

```bash
git clone https://github.com/matt-motik/sp-lms.git
cd sp-lms
uv sync --all-groups
```

Создайте базу данных PostgreSQL:

```bash
psql -U postgres -h localhost -c "CREATE DATABASE sp_lms;"
```

Затем:

```bash
uv run python manage.py migrate
uv run python manage.py createsuperuser
uv run python manage.py runserver
```

Загрузка тестовых данных (курсы, уроки, пользователи, платежи):

```bash
uv run python manage.py loaddata groups payments courses
```

| Пользователь | Пароль | Роль |
|--------------|--------|------|
| `ivan@example.com` | `test12345` | обычный пользователь, владелец курсов и уроков из фикстуры |
| `anna@example.com` | `test12345` | модератор (группа `moderators`) |

Группы назначаются пользователям в админ-панели.

<div id="конфигурация"></div>

## ⚙️ Конфигурация

### Переменные окружения

Скопируйте `.env.example` в `.env` и заполните:

```bash
cp .env.example .env
```

| Переменная | Описание | По умолчанию |
|------------|----------|--------------|
| **SECRET_KEY** | Секретный ключ Django | - |
| **DEBUG** | Режим отладки | False |
| **ALLOWED_HOSTS** | Разрешённые хосты | localhost,127.0.0.1 |
| **DB_NAME** | Имя базы данных PostgreSQL | - |
| **DB_USER** | Пользователь PostgreSQL | - |
| **DB_PASSWORD** | Пароль PostgreSQL | - |
| **DB_HOST** | Хост PostgreSQL | - |
| **DB_PORT** | Порт PostgreSQL | - |

<div id="использование"></div>

## 💻 Использование

### Запуск программы

```bash
uv run python manage.py runserver
```

API доступно по адресу http://127.0.0.1:8000/

### 🔐 Авторизация

Все эндпоинты, кроме регистрации и получения токенов, требуют заголовок:

```
Authorization: Bearer <access>
```

| Метод | URL | Описание |
|-------|-----|----------|
| POST | `/users/register/` | Регистрация (без авторизации) |
| POST | `/users/token/` | Получение пары `access` / `refresh` по email и паролю (без авторизации) |
| POST | `/users/token/refresh/` | Обновление `access` по `refresh` (без авторизации) |

### 🌐 Эндпоинты API

| Метод | URL | Описание |
|-------|-----|----------|
| GET | `/courses/` | Список курсов с количеством и списком уроков |
| POST | `/courses/` | Создание курса |
| GET | `/courses/<id>/` | Просмотр курса |
| PUT / PATCH | `/courses/<id>/` | Изменение курса |
| DELETE | `/courses/<id>/` | Удаление курса |
| GET | `/lessons/` | Список уроков |
| POST | `/lessons/create/` | Создание урока |
| GET | `/lessons/<id>/` | Просмотр урока |
| PUT / PATCH | `/lessons/<id>/update/` | Изменение урока |
| DELETE | `/lessons/<id>/delete/` | Удаление урока |
| POST | `/subscriptions/` | Подписка на курс / отписка, если подписка уже есть. Тело: `{"course": <id>}` |
| GET | `/users/` | Список пользователей (общая информация) |
| GET | `/users/<id>/` | Профиль: свой — полностью с историей платежей, чужой — общая информация |
| PUT / PATCH | `/users/<id>/` | Редактирование своего профиля |
| DELETE | `/users/<id>/` | Удаление своего профиля |
| GET | `/users/payments/` | Список платежей с фильтрацией и сортировкой |

Поля курса в ответе: `lessons_count` — количество уроков, `lessons` — список уроков, `is_subscribed` — подписан ли текущий пользователь на обновления курса.

### 📄 Пагинация

Списки `/courses/` и `/lessons/` выводятся постранично, по 10 элементов. Параметры: `?page=2` — номер страницы, `?page_size=20` — размер страницы (не больше 50).

### 🔗 Валидация ссылок

В `video_url` и `description` урока и в `description` курса можно указывать только ссылки на youtube.com. Ссылка на сторонний ресурс вернёт `400` с описанием ошибки.

### 👥 Права доступа

| Действие | Модератор | Владелец | Другой пользователь |
|----------|-----------|----------|--------------------|
| Создание курса / урока | ❌ | ✅ | ✅ |
| Список курсов / уроков | все | свои | свои |
| Просмотр, редактирование | ✅ любых | ✅ | ❌ |
| Удаление | ❌ | ✅ | ❌ |
| Просмотр чужого профиля | общая информация | — | общая информация |
| Редактирование / удаление профиля | только свой | — | только свой |

Права описаны в `users/permissions.py`: `IsModer`, `IsOwner`, `IsProfileOwner`.

### 🔎 Фильтрация платежей

| Параметр | Пример | Описание |
|----------|--------|----------|
| `ordering` | `?ordering=payment_date` / `?ordering=-payment_date` | Сортировка по дате оплаты по возрастанию / убыванию |
| `paid_course` | `?paid_course=101` | Платежи за курс |
| `paid_lesson` | `?paid_lesson=104` | Платежи за урок |
| `payment_method` | `?payment_method=cash` / `?payment_method=transfer` | Наличные / перевод на счёт |

Параметры можно комбинировать: `/users/payments/?paid_course=101&payment_method=cash`.

Поля с изображениями (`preview`, `avatar`) передаются через `multipart/form-data`.

### 🧪 Проверка в Postman

Коллекция запросов: [`docs/postman/sp-lms.postman_collection.json`](docs/postman/sp-lms.postman_collection.json)

Перед проверкой загрузите фикстуры: `loaddata groups payments courses`. В папке «ДЗ3: права доступа» сначала запустите «1. Регистрация и токены»: токены пользователей сохранятся в переменные коллекции, остальные папки запускаются через **Run folder** и проверяют статусы автотестами.

1. Postman → **Import** → выберите файл коллекции.
2. Запускайте запросы по порядку: курсы → уроки → пользователи, удаление курса последним.
3. В запросах с картинками выберите файл в поле типа **File**.

Адрес сервера задаётся переменной коллекции `base_url`.

## 👤 Админ-панель

Админка доступна по адресу: /admin

Зарегистрированные модели: Course, Lesson, Subscription, CustomUser, Payment

<div id="разработка"></div>

## Разработка

<div id="структура-проекта"></div>

### Структура проекта
<!-- СЕКЦИЯ_AUTO_STRUCTURE: СТАРТ -->
<details>
<summary>📁 Структура проекта (развёрнуть)</summary>

*Этот раздел генерируется автоматически.*

```text
sp-lms/
├── config/
│   ├── __init__.py
│   ├── asgi.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── docs/
│   ├── api/
│   └── postman/
│       └── sp-lms.postman_collection.json
├── lms/
│   ├── fixtures/
│   │   └── courses.json
│   ├── migrations/
│   │   ├── 0001_initial.py
│   │   ├── 0002_course_owner_lesson_owner.py
│   │   ├── 0003_subscription.py
│   │   ├── 0004_ordering.py
│   │   └── __init__.py
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── models.py
│   ├── paginators.py
│   ├── serializers.py
│   ├── tests.py
│   ├── urls.py
│   ├── validators.py
│   └── views.py
├── users/
│   ├── fixtures/
│   │   ├── groups.json
│   │   └── payments.json
│   ├── migrations/
│   │   ├── 0001_initial.py
│   │   ├── 0002_payment.py
│   │   └── __init__.py
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── managers.py
│   ├── models.py
│   ├── permissions.py
│   ├── serializers.py
│   ├── tests.py
│   ├── urls.py
│   └── views.py
├── coverage.txt
├── manage.py
├── pyproject.toml
├── README.md
├── readme_gen.py
└── uv.lock
```

</details>
<!-- СЕКЦИЯ_AUTO_STRUCTURE: КОНЕЦ -->

<div id="линтеры"></div>

### 🔍 Линтеры и форматирование

Проект использует `ruff` для линтинга и форматирования, `mypy` для проверки типов.

### Проверка кода

```bash
# Линтинг
uv run ruff check lms/ users/ config/

# Автоисправление ошибок
uv run ruff check --fix lms/ users/ config/

# Форматирование
uv run ruff format lms/ users/ config/

# Проверка типов
uv run mypy lms/ users/ config/
```

### 🧪 Тесты

Для тестовой базы пользователю PostgreSQL нужно право на создание БД: `ALTER USER "<DB_USER>" CREATEDB;`

```bash
# Запуск тестов
uv run python manage.py test

# Тесты с подсчётом покрытия
uv run coverage run manage.py test
uv run coverage report

# Тесты, отчёт покрытия в coverage.txt и обновление README
uv run python readme_gen.py
```

<!-- СЕКЦИЯ_AUTO_TEST: СТАРТ -->
<details>
<summary>📊 Результаты тестов и покрытие (развёрнуть)</summary>

### 📊 Результаты тестов

```
Ran 55 tests in 27.643s
OK
```

### 📈 Покрытие

```text
Name                   Stmts   Miss  Cover
------------------------------------------
config/__init__.py         0      0   100%
config/settings.py        27      0   100%
config/urls.py             7      1    86%
lms/__init__.py            0      0   100%
lms/admin.py              15      0   100%
lms/apps.py                5      0   100%
lms/models.py             36      3    92%
lms/paginators.py          5      0   100%
lms/serializers.py        29      1    97%
lms/tests.py             244      0   100%
lms/urls.py                7      0   100%
lms/validators.py         21      0   100%
lms/views.py              66      0   100%
users/__init__.py          0      0   100%
users/admin.py            11      0   100%
users/apps.py              5      0   100%
users/managers.py         21      9    57%
users/models.py           35      2    94%
users/permissions.py      21      0   100%
users/serializers.py      50      2    96%
users/tests.py           119      0   100%
users/urls.py              9      0   100%
users/views.py            28      0   100%
------------------------------------------
TOTAL                    761     18    98%
```

> 📄 Отчёт покрытия также сохранён в [`coverage.txt`](coverage.txt)


</details>
<!-- СЕКЦИЯ_AUTO_TEST: КОНЕЦ -->

### Pre-commit hooks

```bash
# Установить hooks (выполняется автоматически перед каждым коммитом)
uv run pre-commit install

# Проверить все файлы вручную
uv run pre-commit run --all-files
```

<!-- СЕКЦИЯ_AUTO_API: СТАРТ -->
<details>
<summary>📚 Документация API (развёрнуть)</summary>

*Этот раздел генерируется автоматически из docstring.*

| Модуль | Функция/Класс | Краткое описание |
|--------|---------------|------------------|
| [**`lms/admin.py`**](docs/api/lms/admin.md) | | |
| | [📦 CourseAdmin](docs/api/lms/admin.md#CourseAdmin) | Настройки админки для курсов. |
| | [📦 LessonAdmin](docs/api/lms/admin.md#LessonAdmin) | Настройки админки для уроков. |
| | [📦 SubscriptionAdmin](docs/api/lms/admin.md#SubscriptionAdmin) | Настройки админки для подписок. |
| [**`lms/apps.py`**](docs/api/lms/apps.md) | | |
| | [📦 LmsConfig](docs/api/lms/apps.md#LmsConfig) | Конфигурация приложения курсов и уроков. |
| [**`lms/models.py`**](docs/api/lms/models.md) | | |
| | [📦 Course](docs/api/lms/models.md#Course) | Модель курса. |
| | [📦 Course.Meta](docs/api/lms/models.md#Course-Meta) | Мета-параметры модели Course. |
| | [📦 Lesson](docs/api/lms/models.md#Lesson) | Модель урока. |
| | [📦 Lesson.Meta](docs/api/lms/models.md#Lesson-Meta) | Мета-параметры модели Lesson. |
| | [📦 Subscription](docs/api/lms/models.md#Subscription) | Модель подписки пользователя на обновления курса. |
| | [📦 Subscription.Meta](docs/api/lms/models.md#Subscription-Meta) | Мета-параметры модели Subscription. |
| [**`lms/paginators.py`**](docs/api/lms/paginators.md) | | |
| | [📦 MaterialsPaginator](docs/api/lms/paginators.md#MaterialsPaginator) | Постраничный вывод курсов и уроков. |
| [**`lms/serializers.py`**](docs/api/lms/serializers.md) | | |
| | [📦 LessonSerializer](docs/api/lms/serializers.md#LessonSerializer) | Сериализатор урока. |
| | [📦 LessonSerializer.Meta](docs/api/lms/serializers.md#LessonSerializer-Meta) | Мета-параметры сериализатора урока. |
| | [📦 CourseSerializer](docs/api/lms/serializers.md#CourseSerializer) | Сериализатор курса с количеством уроков, списком уроков и признаком подписки. |
| | [📦 CourseSerializer.Meta](docs/api/lms/serializers.md#CourseSerializer-Meta) | Мета-параметры сериализатора курса. |
| | [⚙️ CourseSerializer.get_lessons_count](docs/api/lms/serializers.md#CourseSerializer-get_lessons_count) | Возвращает количество уроков курса. |
| | [⚙️ CourseSerializer.get_is_subscribed](docs/api/lms/serializers.md#CourseSerializer-get_is_subscribed) | Возвращает True, если текущий пользователь подписан на обновления курса. |
| | [📦 SubscriptionSerializer](docs/api/lms/serializers.md#SubscriptionSerializer) | Сериализатор подписки: принимает ID курса. |
| | [📦 SubscriptionSerializer.Meta](docs/api/lms/serializers.md#SubscriptionSerializer-Meta) | Мета-параметры сериализатора подписки. |
| [**`lms/validators.py`**](docs/api/lms/validators.md) | | |
| | [🔧 is_youtube_link](docs/api/lms/validators.md#is_youtube_link) | Проверяет, что ссылка ведёт на youtube.com или его поддомен. |
| | [📦 YoutubeLinkValidator](docs/api/lms/validators.md#YoutubeLinkValidator) | Запрещает ссылки на сторонние ресурсы в поле: допускаются только ссылки на youtube.com. |
| [**`lms/views.py`**](docs/api/lms/views.md) | | |
| | [📦 CourseViewSet](docs/api/lms/views.md#CourseViewSet) | CRUD курсов на основе ViewSet. |
| | [⚙️ CourseViewSet.get_queryset](docs/api/lms/views.md#CourseViewSet-get_queryset) | Модератор видит все курсы, остальные пользователи — только свои. |
| | [⚙️ CourseViewSet.get_permissions](docs/api/lms/views.md#CourseViewSet-get_permissions) | Возвращает права для текущего action. |
| | [⚙️ CourseViewSet.perform_create](docs/api/lms/views.md#CourseViewSet-perform_create) | Привязывает создаваемый курс к текущему пользователю. |
| | [📦 LessonCreateAPIView](docs/api/lms/views.md#LessonCreateAPIView) | Создание урока. Модератору недоступно. |
| | [⚙️ LessonCreateAPIView.perform_create](docs/api/lms/views.md#LessonCreateAPIView-perform_create) | Привязывает создаваемый урок к текущему пользователю. |
| | [📦 LessonListAPIView](docs/api/lms/views.md#LessonListAPIView) | Список уроков: модератору все, остальным только свои. |
| | [⚙️ LessonListAPIView.get_queryset](docs/api/lms/views.md#LessonListAPIView-get_queryset) | Модератор видит все уроки, остальные пользователи — только свои. |
| | [📦 LessonRetrieveAPIView](docs/api/lms/views.md#LessonRetrieveAPIView) | Просмотр урока: модератору или владельцу. |
| | [📦 LessonUpdateAPIView](docs/api/lms/views.md#LessonUpdateAPIView) | Редактирование урока: модератору или владельцу. |
| | [📦 LessonDestroyAPIView](docs/api/lms/views.md#LessonDestroyAPIView) | Удаление урока: только владельцу, модератору недоступно. |
| | [📦 SubscriptionAPIView](docs/api/lms/views.md#SubscriptionAPIView) | Подписка на обновления курса: повторный запрос по тому же курсу снимает подписку. |
| | [⚙️ SubscriptionAPIView.post](docs/api/lms/views.md#SubscriptionAPIView-post) | Создаёт подписку, если её нет, и удаляет, если она уже есть. |
| [**`manage.py`**](docs/api/manage.md) | | |
| | [🔧 main](docs/api/manage.md#main) | Run administrative tasks. |
| [**`users/admin.py`**](docs/api/users/admin.md) | | |
| | [📦 CustomUserAdmin](docs/api/users/admin.md#CustomUserAdmin) | Настройки админки для пользователей. |
| | [📦 PaymentAdmin](docs/api/users/admin.md#PaymentAdmin) | Настройки админки для платежей. |
| [**`users/apps.py`**](docs/api/users/apps.md) | | |
| | [📦 UsersConfig](docs/api/users/apps.md#UsersConfig) | Конфигурация приложения пользователей. |
| [**`users/managers.py`**](docs/api/users/managers.md) | | |
| | [📦 CustomUserManager](docs/api/users/managers.md#CustomUserManager) | Менеджер пользователей, использующий email вместо username. |
| | [⚙️ CustomUserManager.create_user](docs/api/users/managers.md#CustomUserManager-create_user) | Создаёт и сохраняет обычного пользователя. |
| | [⚙️ CustomUserManager.create_superuser](docs/api/users/managers.md#CustomUserManager-create_superuser) | Создаёт и сохраняет суперпользователя. |
| [**`users/models.py`**](docs/api/users/models.md) | | |
| | [📦 CustomUser](docs/api/users/models.md#CustomUser) | Кастомная модель пользователя с авторизацией по email. |
| | [📦 CustomUser.Meta](docs/api/users/models.md#CustomUser-Meta) | Мета-параметры модели CustomUser. |
| | [📦 Payment](docs/api/users/models.md#Payment) | Модель платежа за курс или отдельный урок. |
| | [📦 Payment.PaymentMethod](docs/api/users/models.md#Payment-PaymentMethod) | Способы оплаты. |
| | [📦 Payment.Meta](docs/api/users/models.md#Payment-Meta) | Мета-параметры модели Payment. |
| [**`users/permissions.py`**](docs/api/users/permissions.md) | | |
| | [🔧 is_moderator](docs/api/users/permissions.md#is_moderator) | Возвращает True, если пользователь авторизован и входит в группу модераторов. |
| | [📦 IsModer](docs/api/users/permissions.md#IsModer) | Пользователь входит в группу модераторов. |
| | [⚙️ IsModer.has_permission](docs/api/users/permissions.md#IsModer-has_permission) | Проверяет, что пользователь состоит в группе модераторов. |
| | [⚙️ IsModer.has_object_permission](docs/api/users/permissions.md#IsModer-has_object_permission) | Проверяет членство в группе модераторов и на уровне объекта. |
| | [📦 IsOwner](docs/api/users/permissions.md#IsOwner) | Пользователь является владельцем объекта. |
| | [⚙️ IsOwner.has_object_permission](docs/api/users/permissions.md#IsOwner-has_object_permission) | Проверяет, что объект принадлежит текущему пользователю. |
| | [📦 IsProfileOwner](docs/api/users/permissions.md#IsProfileOwner) | Пользователь работает со своим профилем. |
| | [⚙️ IsProfileOwner.has_object_permission](docs/api/users/permissions.md#IsProfileOwner-has_object_permission) | Проверяет, что профиль принадлежит текущему пользователю. |
| [**`users/serializers.py`**](docs/api/users/serializers.md) | | |
| | [📦 PaymentSerializer](docs/api/users/serializers.md#PaymentSerializer) | Сериализатор платежа. |
| | [📦 PaymentSerializer.Meta](docs/api/users/serializers.md#PaymentSerializer-Meta) | Мета-параметры сериализатора платежа. |
| | [📦 PaymentHistorySerializer](docs/api/users/serializers.md#PaymentHistorySerializer) | Сериализатор платежа для истории в профиле: с названиями курса, урока и способа оплаты. |
| | [📦 PaymentHistorySerializer.Meta](docs/api/users/serializers.md#PaymentHistorySerializer-Meta) | Мета-параметры сериализатора истории платежей. |
| | [📦 UserProfileSerializer](docs/api/users/serializers.md#UserProfileSerializer) | Сериализатор профиля пользователя с историей платежей. |
| | [📦 UserProfileSerializer.Meta](docs/api/users/serializers.md#UserProfileSerializer-Meta) | Мета-параметры сериализатора профиля. |
| | [📦 UserPublicSerializer](docs/api/users/serializers.md#UserPublicSerializer) | Сериализатор чужого профиля: только общая информация, без фамилии, пароля и платежей. |
| | [📦 UserPublicSerializer.Meta](docs/api/users/serializers.md#UserPublicSerializer-Meta) | Мета-параметры публичного сериализатора профиля. |
| | [📦 UserRegisterSerializer](docs/api/users/serializers.md#UserRegisterSerializer) | Сериализатор регистрации пользователя. |
| | [📦 UserRegisterSerializer.Meta](docs/api/users/serializers.md#UserRegisterSerializer-Meta) | Мета-параметры сериализатора регистрации. |
| | [⚙️ UserRegisterSerializer.validate_email](docs/api/users/serializers.md#UserRegisterSerializer-validate_email) | Проверяет, что пользователь с таким email ещё не зарегистрирован. |
| | [⚙️ UserRegisterSerializer.validate](docs/api/users/serializers.md#UserRegisterSerializer-validate) | Проверяет пароль стандартными валидаторами Django. |
| | [⚙️ UserRegisterSerializer.create](docs/api/users/serializers.md#UserRegisterSerializer-create) | Создаёт пользователя с хешированным паролем. |
| [**`users/views.py`**](docs/api/users/views.md) | | |
| | [📦 UserRegisterAPIView](docs/api/users/views.md#UserRegisterAPIView) | Регистрация нового пользователя. Доступна без авторизации. |
| | [📦 UserViewSet](docs/api/users/views.md#UserViewSet) | Профили пользователей: смотреть можно любой, редактировать и удалять только свой. |
| | [⚙️ UserViewSet.get_permissions](docs/api/users/views.md#UserViewSet-get_permissions) | Возвращает права для текущего action. |
| | [⚙️ UserViewSet.is_own_profile](docs/api/users/views.md#UserViewSet-is_own_profile) | Проверяет, что запрошен профиль текущего пользователя. |
| | [⚙️ UserViewSet.get_serializer_class](docs/api/users/views.md#UserViewSet-get_serializer_class) | Свой профиль отдаётся полностью, чужой и список — только общая информация. |
| | [📦 PaymentListAPIView](docs/api/users/views.md#PaymentListAPIView) | Список платежей с фильтрацией по курсу, уроку, способу оплаты и сортировкой по дате. |

> 📘 **Полная документация** доступна в папке [`docs/api`](docs/api).

</details>
<!-- СЕКЦИЯ_AUTO_API: КОНЕЦ -->

<div id="to-do"></div>

## To do

- [x] Структура проекта, `pyproject.toml`, `.gitignore`, uv, линтеры
- [x] Инициализация Django-проекта, подключение DRF
- [x] Подключение PostgreSQL, настройка `.env`
- [x] Приложение users, модель `CustomUser` с email как `USERNAME_FIELD`
- [x] Поля пользователя: телефон, город, аватар
- [x] Кастомный менеджер `CustomUserManager`
- [x] Приложение lms, модели `Course` и `Lesson` со связью один-ко-многим
- [x] Миграции и регистрация в админке
- [x] Сериализаторы `CourseSerializer`, `LessonSerializer`, `UserProfileSerializer`
- [x] CRUD курсов на `ModelViewSet`
- [x] CRUD уроков на Generic-классах
- [x] Редактирование профиля пользователя на Generic (доп. задание)
- [x] Раздача медиафайлов в режиме DEBUG
- [x] Проверка эндпоинтов в Postman, экспорт коллекции
- [x] Проверить линтеры (`ruff`, `mypy`), pre-commit
- [x] Обновить README
- [x] Поле `lessons_count` в сериализаторе курса через `SerializerMethodField`
- [x] Вложенный вывод уроков в сериализаторе курса
- [x] Модель `Payment` в приложении users
- [x] Фикстуры курсов, уроков, пользователей и платежей
- [x] Эндпоинт списка платежей с фильтрацией (`django-filter`) и сортировкой по дате
- [x] История платежей в профиле пользователя (доп. задание)
- [x] JWT-авторизация, `IsAuthenticated` по умолчанию
- [x] Регистрация и CRUD пользователей
- [x] Группа модераторов, `IsModer`, фикстура групп
- [x] Права по action во ViewSet и `permission_classes` в Generic
- [x] Поле владельца в курсе и уроке, `perform_create`, `IsOwner`
- [x] Ограничение профилей: чужой — только общая информация, правка только своего (доп. задание)
- [x] Валидатор ссылок на youtube.com для курсов и уроков
- [x] Модель подписки на обновления курса, эндпоинт подписки, признак `is_subscribed`
- [x] Пагинация курсов и уроков
- [x] Тесты CRUD уроков и подписки, отчёт покрытия `coverage.txt`
- [x] Тесты на все эндпоинты проекта (доп. задание)

<div id="команда-проекта"></div>

## Команда проекта

- Matvey Bakirov — [mabakirov@gmail.com](mailto:mabakirov@gmail.com) — Back-End Engineer