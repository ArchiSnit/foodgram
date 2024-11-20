import re
import base64
from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from django.core.exceptions import ValidationError

from users.models import Subscription

from users.constants import (
    # MAX_AMOUNT,
    # MAX_COOKING,
    # MIN_AMOUNT,
    # MIN_COOKING,
    USERNAME_REGEX
)

from recipes.models import (Tag, Ingredient,
                            Recipe, RecipeIngredient,
                            FavoriteRecipe, ShoppingCart
                            )


User = get_user_model()


class Base64ImageField(serializers.ImageField):
    """Для расшифровки изображений (рецепт, аватар)."""

    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]

            # Валидация формата изображения
            if ext not in ['jpeg', 'png', 'gif']:
                raise serializers.ValidationError(
                    "Неподдерживаемый формат изображения.")

            # Декодирование изображения
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)

        return super().to_internal_value(data)


class UserPostSerializer(serializers.ModelSerializer):
    """Сериализатор для создания пользователя"""

    avatar = Base64ImageField(required=False)  # Аватар (если передан)

    class Meta:
        model = User
        fields = ('email', 'id',
                  'username', 'first_name',
                  'last_name', 'avatar', 'password')

    def validate_username(self, value):
        """Проверка на соответствие имени пользователя
            регулярному выражению.
        """
        if not re.match(USERNAME_REGEX, value):
            raise ValidationError('Недопустимый символ в имени пользователя.')
        return value

    def create(self, validated_data):
        """Метод создания пользователя с дополнительными полями."""
        password = validated_data.pop('password', None)
        user = super().create(validated_data)
        if password:
            user.set_password(password)
            user.save()
        return user


class UserGetSerializer(serializers.ModelSerializer):
    """Сериализатор для получения информации о пользователе"""

    class Meta:
        model = User
        fields = ('email', 'id',
                  'username', 'first_name',
                  'last_name', 'avatar'
                  )


class SubscriptionSerializer(serializers.ModelSerializer):
    """Сериализатор для подписок."""

    user = serializers.SlugRelatedField(slug_field='username',
                                        queryset=User.objects.all()
                                        )
    cooker = serializers.SlugRelatedField(slug_field='username',
                                          queryset=User.objects.all()
                                          )

    class Meta:
        model = Subscription
        fields = ('user', 'cooker')

    def validate(self, data):
        """Проверка на подписку на самого себя и уникальность подписки."""
        user = data.get('user')
        cooker = data.get('cooker')

        # Проверяем, не пытается ли пользователь подписаться на самого себя
        if user == cooker:
            raise ValidationError('Нельзя подписаться на самого себя.')

        # Проверяем уникальность подписки (пара "пользователь - повар")
        if Subscription.objects.filter(user=user, cooker=cooker).exists():
            raise ValidationError('Вы уже подписаны на этого пользователя.')

        return data

    def create(self, validated_data):
        """Создание подписки."""
        return Subscription.objects.create(**validated_data)


class SubscriptionListSerializer(serializers.ModelSerializer):
    """Сериализатор для вывода списка подписок пользователя."""

    cooker = serializers.SlugRelatedField(slug_field='username',
                                          queryset=User.objects.all()
                                          )

    class Meta:
        model = Subscription
        fields = ('cooker',)


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор для тегов"""
    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для ингредиентов"""
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class RecipeIngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для отображения ингредиентов в рецепте."""
    id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all())
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit')
    amount = serializers.IntegerField()

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipeSerializer(serializers.ModelSerializer):
    """Основной сериализатор рецептов."""
    author = serializers.StringRelatedField()
    tags = TagSerializer(many=True, read_only=True)
    ingredients = RecipeIngredientSerializer(many=True,
                                             source='recipe_ingredients')
    image = serializers.ImageField()
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            'id', 'name', 'text', 'cooking_time',
            'image', 'author', 'tags', 'ingredients',
            'is_favorited', 'is_in_shopping_cart', 'pub_date'
        )

    def get_is_favorited(self, obj):
        """Проверяет, добавлен ли рецепт в избранное текущим пользователем."""
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return obj.favorited_by.filter(id=user.id).exists()

    def get_is_in_shopping_cart(self, obj):
        """Проверяет, добавлен ли рецепт в корзину текущим пользователем."""
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return obj.in_shopping_cart.filter(id=user.id).exists()

    def validate(self, data):
        """Проверяет, является ли пользователь авторизованным."""
        user = self.context.get('request').user
        if not user.is_authenticated:
            raise serializers.ValidationError(
                'Пользователь должен быть авторизован.')
        return data

    def update(self, instance, validated_data):
        """Обновление рецепта доступно только автору."""
        user = self.context.get('request').user
        if instance.author != user:
            raise serializers.ValidationError(
                'Вы не являетесь автором рецепта.')
        return super().update(instance, validated_data)


class RecipeCreateSerializer(serializers.ModelSerializer):
    """Сериализатор для создания рецептов."""
    tags = serializers.PrimaryKeyRelatedField(queryset=Tag.objects.all(),
                                              many=True
                                              )
    ingredients = RecipeIngredientSerializer(many=True)
    image = serializers.ImageField()

    class Meta:
        model = Recipe
        fields = ('name', 'text',
                  'cooking_time', 'image',
                  'tags', 'ingredients'
                  )

    def create(self, validated_data):
        """Создание рецепта с ингредиентами и тегами."""
        tags = validated_data.pop('tags')
        ingredients_data = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)

        # Добавление ингредиентов через промежуточную модель
        for ingredient in ingredients_data:
            RecipeIngredient.objects.create(
                recipe=recipe,
                ingredient=ingredient['id'],
                amount=ingredient['amount']
            )
        return recipe


class FavoriteRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для добавления рецептов в избранное."""

    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    recipe = serializers.PrimaryKeyRelatedField(queryset=Recipe.objects.all())

    class Meta:
        model = FavoriteRecipe
        fields = ('user', 'recipe')
        validators = [
            serializers.UniqueTogetherValidator(
                queryset=FavoriteRecipe.objects.all(),
                fields=['user', 'recipe'],
                message='Рецепт уже добавлен в избранное'
            )
        ]


class ShoppingCartSerializer(serializers.ModelSerializer):
    """Сериализатор для добавления рецептов в корзину покупок."""

    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    recipe = serializers.PrimaryKeyRelatedField(queryset=Recipe.objects.all())

    class Meta:
        model = ShoppingCart
        fields = ('user', 'recipe')
        validators = [
            serializers.UniqueTogetherValidator(
                queryset=ShoppingCart.objects.all(),
                fields=['user', 'recipe'],
                message='Рецепт уже добавлен в корзину'
            )
        ]
