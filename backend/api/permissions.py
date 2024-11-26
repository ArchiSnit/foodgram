from rest_framework import permissions


class IsAuthorOrReadOnly(permissions.BasePermission):
    """
    Разрешение: Только автор объекта может его изменять,
    остальные могут только просматривать. Также предоставляется доступ
    для суперпользователей.
    """

    def has_object_permission(self, request, view, obj):
        """
        Проверяет права доступа для операций с объектом.
        """
        # Безопасные методы (GET, HEAD, OPTIONS) доступны всем.
        if request.method in permissions.SAFE_METHODS:
            return True

        if request.user and request.user.is_authenticated:
            if request.user.is_superuser:
                return True
            return obj.author == request.user
        return False


# class OwnerOnly(permissions.BasePermission):
#     """
#     Разрешение, которое позволяет доступ только владельцам ресурса.
#
#     Для безопасных методов (GET, HEAD, OPTIONS)
#     доступ предоставляется всем пользователям.
#     Для остальных методов проверяется,
#     является ли текущий пользователь автором данного объекта.
#     """
#     def has_object_permission(self, view, request, obj):
#         if request.method in permissions.SAFE_METHODS:
#             return True
#
#         return obj.author == request.user
#
