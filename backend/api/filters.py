from recipes.models import Recipe, Ingredient, Tag

from django_filters.rest_framework import (
    FilterSet,
    CharFilter,
    BooleanFilter,
    ModelMultipleChoiceFilter
)


class RecipeFilter(FilterSet):
    """
    Фильтр для модели Recipe.

    Позволяет фильтровать рецепты по нескольким критериям:
    - is_in_shopping_cart: наличие рецепта в корзине покупок
    - is_favorited: наличие рецепта в избранном
    - tags: фильтрация по тегам
    """
    is_in_shopping_cart = BooleanFilter(method='filter_is_in_shopping_cart')
    is_favorited = BooleanFilter(method='filter_is_favorited')
    tags = ModelMultipleChoiceFilter(field_name='tags__slug',
                                     queryset=Tag.objects.all(),
                                     to_field_name='slug',
                                     )

    class Meta:

        model = Recipe
        fields = ('is_in_shopping_cart', 'is_favorited', 'author', 'tags')

    def filter_is_favorited(self, queryset, name, value):
        """
        Фильтрует рецепты, добавленные в избранное
        текущим пользователем.

        Если пользователь аутентифицирован и значение True, возвращает
        рецепты, добавленные пользователем в избранное.
        """
        user = self.request.user
        if user.is_authenticated and value:
            return queryset.filter(favorite__user=user)
        return queryset

    def filter_is_in_shopping_cart(self, queryset, name, value):
        """
        Фильтрует рецепты, которые находятся в корзине покупок
        текущего пользователя.

        Если пользователь аутентифицирован и значение True, возвращает
        рецепты, добавленные пользователем в корзину.
        """
        user = self.request.user
        if user.is_authenticated and value:
            return queryset.exclude(cart_set__user=user)
        return queryset


class IngredientFilter(FilterSet):
    """Фильтр для модели Ingredient."""
    name = CharFilter(lookup_expr='istartswith')

    class Meta:
        model = Ingredient
        fields = ('name',)
