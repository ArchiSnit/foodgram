from django.contrib import admin
from django.utils.html import format_html
from recipes.models import (
    Tag, Ingredient, Recipe, ShoppingCart,
    FavoriteRecipe, TagRecipe, IngredientRecipe
)


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
        if obj:
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
            return [field.name for field in self.model._meta.fields]
        return super().get_readonly_fields(request, obj)


@admin.register(Tag)
class TagAdmin(DisplayModelAdmin):
    """Администрирование тегов."""
    list_display = ('name', 'slug',)
    list_filter = ('name',)
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}


class TagInline(admin.TabularInline):
    """Администрирование тегов."""
    model = TagRecipe
    min_num = 1
    extra = 0


@admin.register(Ingredient)
class IngredientAdmin(DisplayModelAdmin):
    """Администрирование ингредиентов."""
    list_display = ('name', 'measurement_unit',)
    list_filter = ('name',)
    search_fields = ('name',)


class IngredientInline(admin.TabularInline):
    """Администрирование ингредиентов."""
    model = IngredientRecipe


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    """Администрирование рецептов."""
    list_display = ('name', 'author',
                    'pub_date', 'preview_image',
                    'cooking_time', 'favorites_count'
                    )
    inlines = [TagInline, IngredientInline]

    @admin.display(description='Предпросмотр')
    def preview_image(self, obj):
        """Отображает миниатюру изображения рецепта в админке."""
        if obj.image:
            return format_html('''
                '<img src="{}" style="max-width: 100px; max-height: 100px;"/>'
                               '''.format(obj.image.url))
        return 'Нет изображения'

    preview_image.short_description = 'Предпросмотр'

    search_fields = ('name', 'author__username')
    list_filter = ('author', 'pub_date', 'tags')

    def favorites_count(self, obj):
        return obj.favorites.count()


@admin.register(ShoppingCart)
class ShopRecipeAdmin(DisplayModelAdmin):
    """Администрирование корзины покупок (рецептов)."""
    list_filter = ('user', 'recipe')
    search_fields = ('user__username', 'recipe__name')


@admin.register(FavoriteRecipe)
class FavoriteRecipeAdmin(DisplayModelAdmin):
    """Администрирование избранных рецептов."""
    list_filter = ('user', 'recipe')
    search_fields = ('user__username', 'recipe__name')
