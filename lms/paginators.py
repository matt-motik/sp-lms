"""Пагинаторы приложения lms."""

from rest_framework.pagination import PageNumberPagination


class MaterialsPaginator(PageNumberPagination):
    """Постраничный вывод курсов и уроков."""

    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 50
    page_query_description = "Номер страницы."
    page_size_query_description = "Количество элементов на странице, по умолчанию 10, не больше 50."
