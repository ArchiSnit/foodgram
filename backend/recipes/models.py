from django.contrib.auth import get_user_model
from django.db import models

from users.constants import MAX_SPLIT_LENGTH
from recipes.validators import real_amount, actual_cooking_time

User = get_user_model()


class Tag(models.Model):
    """Модель тега рецепта."""
    name = models.CharField(
        max_length=100,
        unique=True,
        verbose_name="Название тега"
    )

    slug = models.SlugField(
        max_length=50,
        unique=True,
        verbose_name="Слаг"
    )

    class Meta:
        ordering = ('name',)
        verbose_name = "Тег"
        verbose_name_plural = "Теги"

    def __str__(self):
        return self.name[:MAX_SPLIT_LENGTH]


class Ingredient(models.Model):
    """Модель ингредиента для рецептов."""
    name = models.CharField(
        max_length=255,
        verbose_name="Название ингредиента"
    )
    measurement_unit = models.CharField(
        max_length=50,
        verbose_name="Единица измерения"
    )

    class Meta:
        ordering = ('name',)
        verbose_name = "Ингредиент"
        verbose_name_plural = "Ингредиенты"

    def __str__(self):
        return self.name[:MAX_SPLIT_LENGTH]


class Recipe(models.Model):
    """Модель рецепта."""
    name = models.CharField(
        max_length=255,
        verbose_name="Название рецепта"
    )
    text = models.TextField(
        verbose_name="Описание рецепта"
    )
    cooking_time = models.PositiveIntegerField(
        verbose_name="Время приготовления (в минутах)",
        validators=[actual_cooking_time]
    )
    image = models.ImageField(
        upload_to='recipes/images/',
        verbose_name="Изображение рецепта"
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name="Автор рецепта"
    )
    tags = models.ManyToManyField(
        'Tag',
        related_name='recipes',
        verbose_name="Тег(и) рецепта"
    )
    ingredients = models.ManyToManyField(
        'Ingredient',
        through='RecipeIngredient',
        related_name='recipes',
        verbose_name="Ингредиенты рецепта"
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата публикации"
    )

    class Meta:
        ordering = ('-pub_date',)
        verbose_name = "Рецепт"
        verbose_name_plural = "Рецепты"

    def __str__(self):
        return f'{self.name} by {self.author}'


class RecipeIngredient(models.Model):
    """Связующая модель для ингредиентов в рецепте."""

    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='recipe_ingredients',
        verbose_name="Рецепт"
    )
    ingredient = models.ForeignKey(
        'Ingredient',
        on_delete=models.CASCADE,
        related_name='ingredient_recipes',
        verbose_name="Ингредиент"
    )
    amount = models.PositiveIntegerField(
        verbose_name="Количество ингредиента",
        validators=(real_amount,),
    )

    class Meta:
        verbose_name = "Ингредиент рецепта"
        verbose_name_plural = "Ингредиенты рецептов"
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'ingredient'],
                name='unique_recipe_ingredient'
            )
        ]

    def __str__(self):
        return f'{self.ingredient} для {self.recipe}'


class FavoriteRecipe(models.Model):
    """Модель для избранных рецептов."""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='favorite_recipes',
        verbose_name="Пользователь"
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='favorited_by',
        verbose_name="Рецепт"
    )

    class Meta:
        verbose_name = "Избранный рецепт"
        verbose_name_plural = "Избранные рецепты"
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_user_favorite'
            )
        ]

    def __str__(self):
        return f'{self.user} добавил в избранное {self.recipe}'


class ShoppingCart(models.Model):
    """Модель для рецептов в корзине покупок."""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='shopping_cart',
        verbose_name="Пользователь"
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='in_shopping_cart',
        verbose_name="Рецепт"
    )

    class Meta:
        verbose_name = "Корзина покупок"
        verbose_name_plural = "Корзины покупок"
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_user_shopping_cart'
            )
        ]

    def __str__(self):
        return f'{self.user} добавил в корзину {self.recipe}'


# Возможно лишняя модель
# class RecipeTagAssociation(models.Model):
#     """Связь между рецептом и тегами"""
#
#     recipe_item = models.ForeignKey(
#         Recipe, on_delete=models.CASCADE,
#         verbose_name='Рецепт'
#     )
#     tag_item = models.ForeignKey(
#         Tag, on_delete=models.CASCADE,
#         verbose_name='Тег'
#     )
#
#     class Meta:
#         ordering = ('recipe_item', 'tag_item')
#         verbose_name = 'Тег для рецепта'
#         verbose_name_plural = 'Теги для рецептов'
#         constraints = [
#             models.UniqueConstraint(
#                 fields=['recipe_item', 'tag_item'],
#                 name='unique_recipe_tag_association'
#             )
#         ]
#
#     def __str__(self):
#         return f'Рецепт {self.recipe_item} имеет тег {self.tag_item}'
