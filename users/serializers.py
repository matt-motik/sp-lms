"""Сериализаторы приложения users."""

from rest_framework import serializers

from users.models import CustomUser, Payment


class PaymentSerializer(serializers.ModelSerializer):
    """Сериализатор платежа."""

    class Meta:
        """Мета-параметры сериализатора платежа."""

        model = Payment
        fields = "__all__"


class PaymentHistorySerializer(PaymentSerializer):
    """Сериализатор платежа для истории в профиле: с названиями курса, урока и способа оплаты."""

    paid_course_title = serializers.CharField(source="paid_course.title", read_only=True, default=None)
    paid_lesson_title = serializers.CharField(source="paid_lesson.title", read_only=True, default=None)
    payment_method_display = serializers.CharField(source="get_payment_method_display", read_only=True)

    class Meta:
        """Мета-параметры сериализатора истории платежей."""

        model = Payment
        fields = (
            "id",
            "payment_date",
            "paid_course",
            "paid_course_title",
            "paid_lesson",
            "paid_lesson_title",
            "amount",
            "payment_method",
            "payment_method_display",
        )


class UserProfileSerializer(serializers.ModelSerializer):
    """Сериализатор профиля пользователя с историей платежей."""

    payments = PaymentHistorySerializer(many=True, read_only=True)

    class Meta:
        """Мета-параметры сериализатора профиля."""

        model = CustomUser
        fields = ("id", "email", "first_name", "last_name", "phone", "city", "avatar", "payments")
