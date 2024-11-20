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
        # Если метод запроса безопасный (GET, HEAD, OPTIONS), разрешаем доступ.
        if request.method in permissions.SAFE_METHODS:
            return True

        # Для остальных методов (POST, PUT, DELETE) проверяем,
        # является ли пользователь автором объекта.
        return obj.author == request.user


class IsAuthorOrReadOnly(permissions.BasePermission):
    """
    Разрешение: Только автор объекта может его изменять,
    остальные могут только просматривать.
    """

    def has_object_permission(self, request, view, obj):
        """
        Проверяет права доступа для операций с объектом.
        """
        # Безопасные методы (GET, HEAD, OPTIONS) доступны всем.
        if request.method in permissions.SAFE_METHODS:
            return True

        # Суперпользователь всегда имеет доступ
        if request.user and request.user.is_superuser:
            return True

        # Для остальных методов (POST, PUT, DELETE).
        # Доступ разрешён только автору объекта.
        return obj.author == request.user
