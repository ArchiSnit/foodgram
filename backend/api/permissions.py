from rest_framework import permissions


class OwnerOnly(permissions.BasePermission):
    """
    Разрешение, позволяющее доступ только владельцам объекта.
    """

    def has_object_permission(self, request, view, obj):
        """
        Проверяет, имеет ли пользователь разрешение на доступ к объекту.

        :param request: HTTP-запрос.
        :param view: Представление, обрабатывающее запрос.
        :param obj: Объект, к которому проверяется доступ.
        :return: True, если пользователь имеет доступ;
        False в противном случае.
        """
        # Если метод запроса безопасный (GET, HEAD, OPTIONS), разрешаем доступ
        if request.method in permissions.SAFE_METHODS:
            return True

        # Для остальных методов (POST, PUT, DELETE) проверяем,
        # является ли пользователь автором объекта
        return obj.author == request.user
