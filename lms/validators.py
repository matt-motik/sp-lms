"""Валидаторы приложения lms."""

import re
from typing import Any
from urllib.parse import urlparse

from rest_framework import serializers

ALLOWED_DOMAIN = "youtube.com"
URL_PATTERN = re.compile(r"(?:https?://|www\.)\S+", re.IGNORECASE)


def is_youtube_link(url: str) -> bool:
    """Проверяет, что ссылка ведёт на youtube.com или его поддомен."""
    if not url.lower().startswith(("http://", "https://")):
        url = f"http://{url}"
    host = (urlparse(url).hostname or "").lower()
    return host == ALLOWED_DOMAIN or host.endswith(f".{ALLOWED_DOMAIN}")


class YoutubeLinkValidator:
    """Запрещает ссылки на сторонние ресурсы в поле: допускаются только ссылки на youtube.com."""

    def __init__(self, field: str) -> None:
        """Запоминает имя проверяемого поля."""
        self.field = field

    def __call__(self, attrs: dict[str, Any]) -> None:
        """Ищет в значении поля все ссылки и проверяет каждую."""
        value = attrs.get(self.field)
        if not value:
            return
        for url in URL_PATTERN.findall(str(value)):
            if not is_youtube_link(url):
                raise serializers.ValidationError(
                    {self.field: f"Ссылка {url} недопустима: можно прикреплять только ссылки на youtube.com."}
                )
