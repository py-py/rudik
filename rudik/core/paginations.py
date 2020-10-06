from rest_framework import pagination


class SmallPageNumberPagination(pagination.PageNumberPagination):
    page_size = 10
