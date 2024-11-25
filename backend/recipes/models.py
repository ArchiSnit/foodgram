from django.db import models
from django.contrib.auth import get_user_model
from recipes.constants import MAX_SPLIT_LENGTH, MAX_LENGTH_NAME
from recipes.validators import real_amount, actual_cooking_time

User = get_user_model()


class BaseEntity(models.Model):
    """Модель CommonInfo наследует от базового класса models.Model
       предоставляет общие функциональности для других моделей
    """
    name = models.CharField(
        verbose_name='Наименование',
        max_length=MAX_LENGTH_NAME,
        unique=True
    )

    class Meta:
        abstract = True
        ordering = ['name']

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    """Модель ингредиента для рецепта."""
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


class Recipe(BaseEntity):
    """Модель рецепта, содержащая название,
       описание, ингредиенты, теги и другую информацию."""
    tags = models.ManyToManyField(Tag, through='TagRecipe', verbose_name='Тег')
    author = models.ForeignKey(User, on_delete=models.CASCADE,
                               verbose_name='Автор')
    ingredients = models.ManyToManyField(
        Ingredient, through='IngredientRecipe'
    )
    text = models.TextField('Описание', help_text='Опишите действия')
    cooking_time = models.PositiveSmallIntegerField(
        'Время приготовления', help_text='в минутах',
        validators=[actual_cooking_time]
    )
    image = models.ImageField('Картинка', upload_to='recipes/images/',
                              null=True, default=None)
    pub_date = models.DateTimeField('Дата и время публикации',
                                    auto_now_add=True)

    class Meta(BaseEntity.Meta):
        ordering = ('-pub_date', 'name')
        default_related_name = 'recipes'
        verbose_name = 'рецепт'
        verbose_name_plural = 'Рецепты'


class TagRecipe(models.Model):
    """Модель для связывания тегов с рецептами"""
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE, verbose_name='Рецепт',
        related_name='recipe_tags'
    )
    tag = models.ForeignKey(
        Tag, on_delete=models.CASCADE, verbose_name='Тег',
        related_name='tag_recipes'
    )

    class Meta:
        ordering = ('recipe',)
        verbose_name = 'теги рецептов'
        verbose_name_plural = 'Теги рецептов'
        constraints = [
            models.UniqueConstraint(fields=('recipe', 'tag'),
                                    name='unique_tag')
        ]

    def __str__(self):
        return f'У рецепта {self.recipe.name} тег {self.tag.name}'


class IngredientRecipe(models.Model):
    """Модель для связывания ингредиентов с рецептами"""
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE, verbose_name='Рецепт',
        related_name='recipe_ingredients'
    )
    ingredient = models.ForeignKey(
        Ingredient, on_delete=models.CASCADE, verbose_name='Ингредиент',
        related_name='ingredient_recipes'
    )
    amount = models.PositiveSmallIntegerField(
        'Количество', validators=[real_amount]
    )

    class Meta:
        ordering = ('recipe', 'ingredient')
        verbose_name = 'ингридиенты в рецепте'
        verbose_name_plural = 'Ингридиенты в рецепте'
        constraints = (
            models.UniqueConstraint(fields=('recipe', 'ingredient'),
                                    name='unique_ingredient'),
        )

    def __str__(self):
        return (
            f'{self.ingredient.name} в {self.recipe.name} в количестве '
            f'{self.amount} {self.ingredient.measurement_unit}'
        )


class UserReciperelations(models.Model):
    """Модель для связывания пользователей с рецептами
       (например, в списках избранного или покупок).
    """
    user = models.ForeignKey(
        User, on_delete=models.CASCADE,
        verbose_name='Пользователь',
    )
    recipe = models.ForeignKey(Recipe, verbose_name='Рецепт',
                               on_delete=models.CASCADE,
                               )

    class Meta:
        abstract = True
        constraints = (
            models.UniqueConstraint(fields=('user', 'recipe'),
                                    name='unique recipe in %(class)s'),
        )


class FavoriteRecipe(UserReciperelations):
    """Модель для избранных рецептов пользователя."""
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='favorite_recipes'
    )
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE, related_name='favorites'
    )

    class Meta(UserReciperelations.Meta):
        unique_together = ('user', 'recipe')
        verbose_name = 'избранное'
        verbose_name_plural = 'Избранное'

    def __str__(self):
        return f'{self.recipe.name} в избранном у {self.user.username}'


class ShoppingCart(UserReciperelations):
    """Модель для списка покупок пользователя."""
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='cart_set'
    )
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE, related_name='cart_set'
    )

    class Meta(UserReciperelations.Meta):
        verbose_name = 'список покупок'
        verbose_name_plural = 'Списки покупок'

    def __str__(self):
        return f'{self.recipe.name} в корзине у {self.user.username}'
