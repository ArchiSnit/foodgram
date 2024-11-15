from django_filters import rest_framework as filters
from recipes.models import Ingredient, Recipe
from django.contrib.auth import get_user_model

User = get_user_model()


class IngredientFilter(filters.FilterSet):
    """Фильтр для ингредиентов.

    Позволяет фильтровать список ингредиентов по названию.
    """

    name = filters.CharFilter(
        field_name='name',
        lookup_expr='istartswith',
        label='Название ингредиента'
    )

    class Meta:
        model = Ingredient
        fields = ('name',)


class RecipeFilter(filters.FilterSet):
    """Фильтр для рецептов.

    Позволяет фильтровать рецепты по различным критериям, таким как автор,
    теги, наличие в списке покупок и избранное.
    """

    author = filters.ModelChoiceFilter(
        field_name='author',
        label='Автор',
        queryset=User.objects.all(),
    )

    tags = filters.AllValuesMultipleFilter(
        label='Теги',
        field_name='tags__slug',
    )

    is_in_shopping_cart = filters.BooleanFilter(
        label='В списке покупок',
        method='filter_is_in_shopping_cart'
    )

    is_favorited = filters.BooleanFilter(
        label='В избранном',
        method='filter_is_favorited'
    )

    class Meta:
        model = Recipe
        fields = ('author', 'tags', 'is_in_shopping_cart', 'is_favorited')

    def filter_is_in_shopping_cart(self, queryset, name, value):
        """Фильтрует рецепты в зависимости от наличия в списке покупок.

        Если значение True и пользователь не анонимен,
        возвращает рецепты, которые находятся в списке покупок пользователя.

        Args:
            queryset: Исходный набор запросов для фильтрации.
            name: Имя поля, по которому происходит фильтрация.
            value: True или False, указывающее, нужно ли фильтровать.

        Returns:
            Отфильтрованный queryset рецептов.
        """
        user = self.request.user
        if value and not user.is_anonymous:
            return queryset.filter(shopper__user=user)
        return queryset

    def filter_is_favorited(self, queryset, name, value):
        """Фильтрует рецепты, добавленные в избранное.

        Если значение True и пользователь не анонимен,
        возвращает рецепты, которые добавлены в избранное пользователем.

        Args:
            queryset: Исходный набор запросов для фильтрации.
            name: Имя поля, по которому происходит фильтрация.
            value: True или False, указывающее, нужно ли фильтровать.

        Returns:
            Отфильтрованный queryset рецептов.
        """
        user = self.request.user
        if value and not user.is_anonymous:
            return queryset.filter(liked__user=user)
        return queryset
