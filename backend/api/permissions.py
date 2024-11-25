# from rest_framework import permissions

# 
# class IsAuthorOrReadOnly(permissions.BasePermission):
#     """
#     Разрешение: Только автор объекта может его изменять,
#     остальные могут только просматривать. Также предоставляется доступ
#     для суперпользователей и администраторов.
#     """
# 
#     def has_object_permission(self, request, view, obj):
#         """
#         Проверяет права доступа для операций с объектом.
#         """
#         # Безопасные методы (GET, HEAD, OPTIONS) доступны всем.
#         if request.method in permissions.SAFE_METHODS:
#             return True
# 
#         # Суперпользователь всегда имеет доступ
#         if request.user and request.user.is_superuser:
#             return True
# 
#         # Проверяем доступ для администраторов или модераторов
#         if request.user and (request.user.is_superuser or request.user.is_staff):
#             return True
# 
#         # Доступ разрешён только автору объекта для остальных методов (POST, PUT, DELETE).
#         return obj.author == request.user

# class IsAuthorOrReadOnly(permissions.BasePermission):
#     """
#     Разрешение, позволяющее автору объекта изменять его,
#     а для всех остальных — только читать.
# 
#     Пользователи могут выполнять только безопасные методы
#     (GET, HEAD или OPTIONS), если они не являются автором объекта.
#     """
# 
#     def has_object_permission(self, request, view, obj):
#         return (request.method in permissions.SAFE_METHODS
#                 or obj.author == request.user)

# возможно нужен

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

        # Если пользователь аутентифицирован
        if request.user and request.user.is_authenticated:
            # Суперпользователь всегда имеет доступ
            if request.user.is_superuser:
                return True

            # Доступ разрешён только автору объекта для остальных методов (POST, PUT, DELETE).
            return obj.author == request.user

        # Неавторизованным пользователям доступ запрещён
        return False


class OwnerOnly(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True

        return obj.author == request.user