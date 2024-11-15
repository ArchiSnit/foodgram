from django.contrib import admin
from django.contrib.auth import get_user_model
from django.utils.html import format_html

from recipes.models import (
    Ingredient,
    Recipe,
    Subscription,
    Tag,
    ShopRecipe,
    FavoriteRecipe,
)


User = get_user_model()


class DisplayModelAdmin(admin.ModelAdmin):
    """Отображает все поля для любой модели."""

    def __init__(self, model, admin_site):
        """Для отображения списка полей."""
        self.list_display = [
            field.name for field in model._meta.fields if field.name != 'id'
        ]
        super().__init__(model, admin_site)

    def get_readonly_fields(self, request, obj=None):
        if obj:  # Если объект уже существует (редактирование)
            # Получаем все названия полей модели
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

    def preview_avatar(self, obj):
        """Отображает миниатюру аватара пользователя в админке."""
        if obj.avatar:  # Проверяем, что у объекта есть аватар
            return format_html('''
                <img src="{}" style="max-width: 100px; max-height: 100px;"/>
                               '''.format(obj.avatar.url))

        return 'Нет изображения'
    # Название столбца
    preview_avatar.short_description = 'Предпросмотр аватара'


@admin.register(Subscription)
class SubscriptionAdmin(DisplayModelAdmin):
    """Администрирование подписок."""


@admin.register(Tag)
class TagAdmin(DisplayModelAdmin):
    """Администрирование тегов."""


@admin.register(Ingredient)
class IngredientAdmin(DisplayModelAdmin):
    """Администрирование ингредиентов."""
    search_fields = ('name',)


class TagInline(admin.TabularInline):
    model = Recipe.tags.through


class IngredientInline(admin.TabularInline):
    model = Recipe.ingredients.through


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    """Администрирование рецептов."""

    # Вывод полей в списке админки
    list_display = ('name', 'author',
                    'pub_date', 'preview_image',
                    'cooking_time'
                    )
    inlines = [TagInline,
               IngredientInline
               ]  # Настройка inline моделей для тегов и ингредиентов

    # Метод для отображения миниатюры изображения
    def preview_image(self, obj):
        """Отображает миниатюру изображения рецепта в админке."""
        if obj.image:  # Проверяем, что у объекта есть изображение
            return format_html('''
                '<img src="{}" style="max-width: 100px; max-height: 100px;"/>'
                               '''.format(obj.image.url))
        return 'Нет изображения'

    preview_image.short_description = 'Предпросмотр'  # Название столбца

    search_fields = ('name',
                     'author__username'
                     )  # Поиск по имени рецепта и имени пользователя автора

    list_filter = ('author',
                   'pub_date',
                   'tags')  # Фильтрация по автору, дате и тегам

    def favorites_count(self, obj):
        return obj.favorite_recipes.count()


@admin.register(ShopRecipe)
class ShopRecipeAdmin(DisplayModelAdmin):
    """Администрирование покупок рецептов."""


@admin.register(FavoriteRecipe)
class FavoriteRecipeAdmin(DisplayModelAdmin):
    """Администрирование избранных рецептов."""
