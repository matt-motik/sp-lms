"""Тесты приложения lms: CRUD уроков и курсов, подписки, валидация ссылок, пагинация."""

from django.contrib.auth.models import Group
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from lms.models import Course, Lesson, Subscription
from lms.validators import is_youtube_link
from users.models import CustomUser
from users.permissions import MODERATORS_GROUP

YOUTUBE_URL = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"


class LmsTestCase(APITestCase):
    """Общие тестовые данные: владелец, чужой пользователь, модератор, курс и урок."""

    def setUp(self) -> None:
        """Создаёт пользователей, курс и урок."""
        self.owner = CustomUser.objects.create_user(email="owner@test.ru", password="pass12345")
        self.other = CustomUser.objects.create_user(email="other@test.ru", password="pass12345")
        self.moder = CustomUser.objects.create_user(email="moder@test.ru", password="pass12345")
        self.moder.groups.add(Group.objects.create(name=MODERATORS_GROUP))

        self.course = Course.objects.create(title="Python", description="Основы", owner=self.owner)
        self.lesson = Lesson.objects.create(
            course=self.course, title="Переменные", video_url=YOUTUBE_URL, owner=self.owner
        )


class LessonTestCase(LmsTestCase):
    """CRUD уроков для владельца, чужого пользователя, модератора и анонима."""

    def test_lesson_create(self) -> None:
        """Пользователь создаёт урок, владельцем становится он сам."""
        self.client.force_authenticate(self.other)
        data = {"course": self.course.pk, "title": "Циклы", "video_url": YOUTUBE_URL}
        response = self.client.post(reverse("lms:lesson-create"), data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.json()["owner"], self.other.pk)
        self.assertEqual(Lesson.objects.count(), 2)

    def test_lesson_create_moder_forbidden(self) -> None:
        """Модератор не может создавать уроки."""
        self.client.force_authenticate(self.moder)
        data = {"course": self.course.pk, "title": "Циклы"}
        response = self.client.post(reverse("lms:lesson-create"), data)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Lesson.objects.count(), 1)

    def test_lesson_create_anonymous(self) -> None:
        """Аноним не может создавать уроки."""
        data = {"course": self.course.pk, "title": "Циклы"}
        response = self.client.post(reverse("lms:lesson-create"), data)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_lesson_create_foreign_link(self) -> None:
        """Ссылка не на youtube.com не проходит валидацию."""
        self.client.force_authenticate(self.owner)
        data = {"course": self.course.pk, "title": "Циклы", "video_url": "https://skillbox.ru/video/1"}
        response = self.client.post(reverse("lms:lesson-create"), data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("video_url", response.json())
        self.assertEqual(Lesson.objects.count(), 1)

    def test_lesson_create_foreign_link_in_description(self) -> None:
        """Ссылка на сторонний ресурс в описании урока не проходит валидацию."""
        self.client.force_authenticate(self.owner)
        data = {"course": self.course.pk, "title": "Циклы", "description": "Подробнее на www.stepik.org/course"}
        response = self.client.post(reverse("lms:lesson-create"), data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("description", response.json())

    def test_lesson_list_owner(self) -> None:
        """Владелец видит свои уроки постранично."""
        self.client.force_authenticate(self.owner)
        response = self.client.get(reverse("lms:lesson-list"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()["count"], 1)
        self.assertEqual(response.json()["results"][0]["title"], self.lesson.title)

    def test_lesson_list_other(self) -> None:
        """Чужой пользователь не видит уроки владельца."""
        self.client.force_authenticate(self.other)
        response = self.client.get(reverse("lms:lesson-list"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()["count"], 0)

    def test_lesson_list_moder(self) -> None:
        """Модератор видит все уроки."""
        Lesson.objects.create(course=self.course, title="Чужой урок", owner=self.other)
        self.client.force_authenticate(self.moder)
        response = self.client.get(reverse("lms:lesson-list"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()["count"], 2)

    def test_lesson_list_pagination(self) -> None:
        """Список уроков разбивается на страницы, размер страницы задаётся параметром page_size."""
        for number in range(14):
            Lesson.objects.create(course=self.course, title=f"Урок {number}", owner=self.owner)
        self.client.force_authenticate(self.owner)

        response = self.client.get(reverse("lms:lesson-list"))
        self.assertEqual(response.json()["count"], 15)
        self.assertEqual(len(response.json()["results"]), 10)
        self.assertIsNotNone(response.json()["next"])

        response = self.client.get(reverse("lms:lesson-list"), {"page_size": 5, "page": 3})
        self.assertEqual(len(response.json()["results"]), 5)
        self.assertIsNone(response.json()["next"])

    def test_lesson_retrieve_owner(self) -> None:
        """Владелец получает свой урок."""
        self.client.force_authenticate(self.owner)
        response = self.client.get(reverse("lms:lesson-detail", args=(self.lesson.pk,)))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()["title"], self.lesson.title)

    def test_lesson_retrieve_moder(self) -> None:
        """Модератор получает любой урок."""
        self.client.force_authenticate(self.moder)
        response = self.client.get(reverse("lms:lesson-detail", args=(self.lesson.pk,)))

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_lesson_retrieve_other_forbidden(self) -> None:
        """Чужой пользователь не может получить урок."""
        self.client.force_authenticate(self.other)
        response = self.client.get(reverse("lms:lesson-detail", args=(self.lesson.pk,)))

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_lesson_retrieve_not_found(self) -> None:
        """Несуществующий урок возвращает 404."""
        self.client.force_authenticate(self.owner)
        response = self.client.get(reverse("lms:lesson-detail", args=(999,)))

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_lesson_update_owner(self) -> None:
        """Владелец редактирует свой урок."""
        self.client.force_authenticate(self.owner)
        response = self.client.patch(reverse("lms:lesson-update", args=(self.lesson.pk,)), {"title": "Типы данных"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.lesson.refresh_from_db()
        self.assertEqual(self.lesson.title, "Типы данных")

    def test_lesson_update_moder(self) -> None:
        """Модератор редактирует любой урок."""
        self.client.force_authenticate(self.moder)
        response = self.client.patch(reverse("lms:lesson-update", args=(self.lesson.pk,)), {"title": "Типы данных"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_lesson_update_other_forbidden(self) -> None:
        """Чужой пользователь не может редактировать урок."""
        self.client.force_authenticate(self.other)
        response = self.client.patch(reverse("lms:lesson-update", args=(self.lesson.pk,)), {"title": "Типы данных"})

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.lesson.refresh_from_db()
        self.assertEqual(self.lesson.title, "Переменные")

    def test_lesson_update_foreign_link(self) -> None:
        """При редактировании тоже нельзя указать ссылку не на youtube.com."""
        self.client.force_authenticate(self.owner)
        response = self.client.patch(
            reverse("lms:lesson-update", args=(self.lesson.pk,)), {"video_url": "https://vimeo.com/123"}
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.lesson.refresh_from_db()
        self.assertEqual(self.lesson.video_url, YOUTUBE_URL)

    def test_lesson_delete_owner(self) -> None:
        """Владелец удаляет свой урок."""
        self.client.force_authenticate(self.owner)
        response = self.client.delete(reverse("lms:lesson-delete", args=(self.lesson.pk,)))

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Lesson.objects.exists())

    def test_lesson_delete_moder_forbidden(self) -> None:
        """Модератор не может удалять уроки."""
        self.client.force_authenticate(self.moder)
        response = self.client.delete(reverse("lms:lesson-delete", args=(self.lesson.pk,)))

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(Lesson.objects.exists())

    def test_lesson_delete_other_forbidden(self) -> None:
        """Чужой пользователь не может удалить урок."""
        self.client.force_authenticate(self.other)
        response = self.client.delete(reverse("lms:lesson-delete", args=(self.lesson.pk,)))

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(Lesson.objects.exists())


class CourseTestCase(LmsTestCase):
    """CRUD курсов на ViewSet для разных групп пользователей."""

    def test_course_create(self) -> None:
        """Пользователь создаёт курс, владельцем становится он сам."""
        self.client.force_authenticate(self.other)
        response = self.client.post(reverse("lms:courses-list"), {"title": "Django"})

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.json()["owner"], self.other.pk)

    def test_course_create_moder_forbidden(self) -> None:
        """Модератор не может создавать курсы."""
        self.client.force_authenticate(self.moder)
        response = self.client.post(reverse("lms:courses-list"), {"title": "Django"})

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_course_create_foreign_link(self) -> None:
        """Ссылка на сторонний ресурс в описании курса не проходит валидацию."""
        self.client.force_authenticate(self.owner)
        data = {"title": "Django", "description": "Материалы: https://example.com/django"}
        response = self.client.post(reverse("lms:courses-list"), data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("description", response.json())

    def test_course_create_youtube_link(self) -> None:
        """Ссылка на youtube.com в описании курса допустима."""
        self.client.force_authenticate(self.owner)
        data = {"title": "Django", "description": f"Вводное видео: {YOUTUBE_URL}"}
        response = self.client.post(reverse("lms:courses-list"), data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_course_price(self) -> None:
        """Цена курса сохраняется и отдаётся в ответе."""
        self.client.force_authenticate(self.owner)
        response = self.client.post(reverse("lms:courses-list"), {"title": "Django", "price": "25000.00"})

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.json()["price"], "25000.00")

    def test_course_negative_price(self) -> None:
        """Отрицательная цена курса не проходит валидацию."""
        self.client.force_authenticate(self.owner)
        response = self.client.post(reverse("lms:courses-list"), {"title": "Django", "price": "-1"})

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("price", response.json())

    def test_course_list(self) -> None:
        """Владелец видит свои курсы постранично, чужой пользователь — нет, модератор — все."""
        self.client.force_authenticate(self.owner)
        response = self.client.get(reverse("lms:courses-list"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()["count"], 1)
        self.assertEqual(response.json()["results"][0]["lessons_count"], 1)

        self.client.force_authenticate(self.other)
        self.assertEqual(self.client.get(reverse("lms:courses-list")).json()["count"], 0)

        self.client.force_authenticate(self.moder)
        self.assertEqual(self.client.get(reverse("lms:courses-list")).json()["count"], 1)

    def test_course_retrieve(self) -> None:
        """Курс доступен владельцу и модератору, но не чужому пользователю."""
        url = reverse("lms:courses-detail", args=(self.course.pk,))

        self.client.force_authenticate(self.owner)
        self.assertEqual(self.client.get(url).status_code, status.HTTP_200_OK)

        self.client.force_authenticate(self.moder)
        self.assertEqual(self.client.get(url).status_code, status.HTTP_200_OK)

        self.client.force_authenticate(self.other)
        self.assertEqual(self.client.get(url).status_code, status.HTTP_403_FORBIDDEN)

    def test_course_update(self) -> None:
        """Курс редактируют владелец и модератор, чужой пользователь — нет."""
        url = reverse("lms:courses-detail", args=(self.course.pk,))

        self.client.force_authenticate(self.owner)
        self.assertEqual(self.client.patch(url, {"title": "Python 3"}).status_code, status.HTTP_200_OK)

        self.client.force_authenticate(self.moder)
        self.assertEqual(self.client.patch(url, {"title": "Python 3.14"}).status_code, status.HTTP_200_OK)

        self.client.force_authenticate(self.other)
        self.assertEqual(self.client.patch(url, {"title": "Чужой"}).status_code, status.HTTP_403_FORBIDDEN)

        self.course.refresh_from_db()
        self.assertEqual(self.course.title, "Python 3.14")

    def test_course_delete(self) -> None:
        """Курс удаляет только владелец."""
        url = reverse("lms:courses-detail", args=(self.course.pk,))

        self.client.force_authenticate(self.moder)
        self.assertEqual(self.client.delete(url).status_code, status.HTTP_403_FORBIDDEN)

        self.client.force_authenticate(self.other)
        self.assertEqual(self.client.delete(url).status_code, status.HTTP_403_FORBIDDEN)

        self.client.force_authenticate(self.owner)
        self.assertEqual(self.client.delete(url).status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Course.objects.exists())


class SubscriptionTestCase(LmsTestCase):
    """Подписка на обновления курса."""

    def setUp(self) -> None:
        """Добавляет адрес эндпоинта подписки."""
        super().setUp()
        self.url = reverse("lms:subscription")

    def test_subscription_create(self) -> None:
        """Первый запрос создаёт подписку."""
        self.client.force_authenticate(self.other)
        response = self.client.post(self.url, {"course": self.course.pk})

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.json(), {"message": "Подписка на курс «Python» добавлена."})
        self.assertTrue(Subscription.objects.filter(user=self.other, course=self.course).exists())

    def test_subscription_delete(self) -> None:
        """Повторный запрос удаляет подписку."""
        Subscription.objects.create(user=self.other, course=self.course)
        self.client.force_authenticate(self.other)
        response = self.client.post(self.url, {"course": self.course.pk})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json(), {"message": "Подписка на курс «Python» удалена."})
        self.assertFalse(Subscription.objects.exists())

    def test_subscription_only_own(self) -> None:
        """Отписка пользователя не затрагивает подписки других пользователей."""
        Subscription.objects.create(user=self.owner, course=self.course)
        self.client.force_authenticate(self.other)
        self.client.post(self.url, {"course": self.course.pk})

        self.assertEqual(Subscription.objects.filter(course=self.course).count(), 2)

    def test_subscription_moder(self) -> None:
        """Модератор тоже может подписаться на курс."""
        self.client.force_authenticate(self.moder)
        response = self.client.post(self.url, {"course": self.course.pk})

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_subscription_course_not_found(self) -> None:
        """Подписка на несуществующий курс возвращает ошибку."""
        self.client.force_authenticate(self.other)
        response = self.client.post(self.url, {"course": 999})

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("course", response.json())

    def test_subscription_without_course(self) -> None:
        """Запрос без курса возвращает ошибку."""
        self.client.force_authenticate(self.other)
        response = self.client.post(self.url, {})

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_subscription_anonymous(self) -> None:
        """Аноним не может подписаться."""
        response = self.client.post(self.url, {"course": self.course.pk})

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertFalse(Subscription.objects.exists())

    def test_course_is_subscribed(self) -> None:
        """Курс отдаёт признак подписки текущего пользователя."""
        url = reverse("lms:courses-detail", args=(self.course.pk,))
        self.client.force_authenticate(self.owner)
        self.assertFalse(self.client.get(url).json()["is_subscribed"])

        Subscription.objects.create(user=self.owner, course=self.course)
        self.assertTrue(self.client.get(url).json()["is_subscribed"])

        Subscription.objects.filter(user=self.owner).delete()
        Subscription.objects.create(user=self.other, course=self.course)
        self.assertFalse(self.client.get(url).json()["is_subscribed"])


class YoutubeLinkTestCase(APITestCase):
    """Проверка ссылок на youtube.com."""

    def test_is_youtube_link(self) -> None:
        """Разрешены youtube.com и его поддомены, остальные домены запрещены."""
        self.assertTrue(is_youtube_link("https://youtube.com/watch?v=1"))
        self.assertTrue(is_youtube_link("https://m.youtube.com/watch?v=1"))
        self.assertTrue(is_youtube_link("www.youtube.com/watch?v=1"))
        self.assertFalse(is_youtube_link("https://skillbox.ru/course"))
        self.assertFalse(is_youtube_link("https://youtube.com.evil.ru/watch"))
        self.assertFalse(is_youtube_link("https://notyoutube.com/watch"))
