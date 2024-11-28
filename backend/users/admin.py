from django.contrib import admin
from django.utils.html import format_html
from django.contrib.auth import get_user_model
from users.models import Subscription

User = get_user_model()


class DisplayModelAdmin(admin.ModelAdmin):
    """Отображает все поля для любой модели."""

    def __init__(self, model, admin_site):
        """
        Инициализация класса DisplayModelAdmin.

        Аргументы:
        model -- модель, для которой создается админ-интерфейс
        admin_site -- экземпляр admin.site,
        к которому относится данный админ-интерфейс

        Для отображения списка полей используется
        все поля модели, кроме поля 'id'.
        """
        self.list_display = [
            field.name for field in model._meta.fields if field.name != 'id'
        ]
        super().__init__(model, admin_site)

    def get_readonly_fields(self, request, obj=None):
        """
        Получает список полей, доступных только для чтения.

        Аргументы:
        request -- текущий HTTP запрос
        obj -- объект модели для редактирования,
        если это редактирование существующего объекта,
        иначе None

        Если объект уже существует (редактирование),
        возвращает все поля модели как доступные
        только для чтения.
        В противном случае используется стандартный функционал.
        """
        if obj:
            return [field.name for field in self.model._meta.fields]
        return super().get_readonly_fields(request, obj)


@admin.register(User)
class UserAdmin(DisplayModelAdmin):
    """Администрирование пользователей."""

    search_fields = ('username', 'first_name',
                     'last_name', 'email'
                     )

    # Определяем, какие поля отображать в админке
    list_display = ('username', 'first_name',
                    'last_name', 'email', 'preview_avatar'
                    )

    @admin.display(description='Предпросмотр')
    def preview_avatar(self, obj):
        """Отображает миниатюру аватара пользователя в админке."""
        if obj.avatar:
            return format_html('''
                <img src="{}" style="max-width: 100px; max-height: 100px;"/>
                               '''.format(obj.avatar.url))

        return 'Нет изображения'
    # Название столбца
    preview_avatar.short_description = 'Предпросмотр аватара'


@admin.register(Subscription)
class SubscriptionAdmin(DisplayModelAdmin):
    """Администрирование подписок."""

    list_filter = ('user', 'cooker')
    search_fields = ('user__username', 'cooker__username')
