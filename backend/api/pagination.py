from rest_framework.pagination import PageNumberPagination


class CustomPageNumberPagination(PageNumberPagination):
    """Кастомная пагинация."""

    page_size_query_param = 'limit'
