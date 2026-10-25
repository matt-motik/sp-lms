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
- **Админ-панель** для курсов, уроков, пользователей и платежей

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
uv run python manage.py loaddata courses payments
```

Пароль тестовых пользователей `ivan@example.com` и `anna@example.com`: `test12345`.

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
| GET | `/users/<id>/` | Профиль пользователя с историей платежей |
| PUT / PATCH | `/users/<id>/` | Редактирование профиля пользователя |
| GET | `/users/payments/` | Список платежей с фильтрацией и сортировкой |

Поля курса в ответе: `lessons_count` — количество уроков, `lessons` — список уроков.

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

Для запросов к платежам сначала загрузите фикстуры: loaddata courses payments.

1. Postman → **Import** → выберите файл коллекции.
2. Запускайте запросы по порядку: курсы → уроки → пользователи, удаление курса последним.
3. В запросах с картинками выберите файл в поле типа **File**.

Адрес сервера задаётся переменной коллекции `base_url`.

## 👤 Админ-панель

Админка доступна по адресу: /admin

Зарегистрированные модели: Course, Lesson, CustomUser, Payment

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
│   │   └── __init__.py
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── models.py
│   ├── serializers.py
│   ├── urls.py
│   └── views.py
├── users/
│   ├── fixtures/
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
│   ├── serializers.py
│   ├── urls.py
│   └── views.py
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
| [**`lms/apps.py`**](docs/api/lms/apps.md) | | |
| | [📦 LmsConfig](docs/api/lms/apps.md#LmsConfig) | Конфигурация приложения курсов и уроков. |
| [**`lms/models.py`**](docs/api/lms/models.md) | | |
| | [📦 Course](docs/api/lms/models.md#Course) | Модель курса. |
| | [📦 Course.Meta](docs/api/lms/models.md#Course-Meta) | Мета-параметры модели Course. |
| | [📦 Lesson](docs/api/lms/models.md#Lesson) | Модель урока. |
| | [📦 Lesson.Meta](docs/api/lms/models.md#Lesson-Meta) | Мета-параметры модели Lesson. |
| [**`lms/serializers.py`**](docs/api/lms/serializers.md) | | |
| | [📦 LessonSerializer](docs/api/lms/serializers.md#LessonSerializer) | Сериализатор урока. |
| | [📦 LessonSerializer.Meta](docs/api/lms/serializers.md#LessonSerializer-Meta) | Мета-параметры сериализатора урока. |
| | [📦 CourseSerializer](docs/api/lms/serializers.md#CourseSerializer) | Сериализатор курса с количеством уроков и списком уроков. |
| | [📦 CourseSerializer.Meta](docs/api/lms/serializers.md#CourseSerializer-Meta) | Мета-параметры сериализатора курса. |
| | [⚙️ CourseSerializer.get_lessons_count](docs/api/lms/serializers.md#CourseSerializer-get_lessons_count) | Возвращает количество уроков курса. |
| [**`lms/views.py`**](docs/api/lms/views.md) | | |
| | [📦 CourseViewSet](docs/api/lms/views.md#CourseViewSet) | CRUD курсов на основе ViewSet. |
| | [📦 LessonCreateAPIView](docs/api/lms/views.md#LessonCreateAPIView) | Создание урока. |
| | [📦 LessonListAPIView](docs/api/lms/views.md#LessonListAPIView) | Список уроков. |
| | [📦 LessonRetrieveAPIView](docs/api/lms/views.md#LessonRetrieveAPIView) | Просмотр одного урока. |
| | [📦 LessonUpdateAPIView](docs/api/lms/views.md#LessonUpdateAPIView) | Редактирование урока. |
| | [📦 LessonDestroyAPIView](docs/api/lms/views.md#LessonDestroyAPIView) | Удаление урока. |
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
| [**`users/serializers.py`**](docs/api/users/serializers.md) | | |
| | [📦 PaymentSerializer](docs/api/users/serializers.md#PaymentSerializer) | Сериализатор платежа. |
| | [📦 PaymentSerializer.Meta](docs/api/users/serializers.md#PaymentSerializer-Meta) | Мета-параметры сериализатора платежа. |
| | [📦 PaymentHistorySerializer](docs/api/users/serializers.md#PaymentHistorySerializer) | Сериализатор платежа для истории в профиле: с названиями курса, урока и способа оплаты. |
| | [📦 PaymentHistorySerializer.Meta](docs/api/users/serializers.md#PaymentHistorySerializer-Meta) | Мета-параметры сериализатора истории платежей. |
| | [📦 UserProfileSerializer](docs/api/users/serializers.md#UserProfileSerializer) | Сериализатор профиля пользователя с историей платежей. |
| | [📦 UserProfileSerializer.Meta](docs/api/users/serializers.md#UserProfileSerializer-Meta) | Мета-параметры сериализатора профиля. |
| [**`users/views.py`**](docs/api/users/views.md) | | |
| | [📦 UserProfileAPIView](docs/api/users/views.md#UserProfileAPIView) | Просмотр и редактирование профиля любого пользователя с историей платежей. |
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

<div id="команда-проекта"></div>

## Команда проекта

- Matvey Bakirov — [mabakirov@gmail.com](mailto:mabakirov@gmail.com) — Back-End Engineer