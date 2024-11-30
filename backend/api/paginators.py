from rest_framework.pagination import PageNumberPagination


class LimitPageNumberPaginator(PageNumberPagination):
    """Пользовательская пагинация с ограничением на размер страницы.

    Этот класс расширяет стандартный класс PageNumberPagination
    и позволяет задавать размер страницы через URL параметр 'limit'.
    """
    page_size_query_param = 'limit'
    page_size = 6
