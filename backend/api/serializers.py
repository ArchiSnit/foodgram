import re
from rest_framework import serializers
from django.contrib.auth import get_user_model
from rest_framework.validators import UniqueTogetherValidator

from users.models import Subscription
from api.utils import Base64ImageField

from recipes.models import (Tag, Ingredient,
                            Recipe, IngredientRecipe
                            )


User = get_user_model()


class AvatarSerializer(serializers.Serializer):
    """Обрабатывает изображение аватара, закодированное в Base64.
       C использованием Base64ImageField для валидации и хранения.
    """
    avatar = Base64ImageField()


class UserSerializer(serializers.ModelSerializer):
    """Общий сериализатор пользователя
       Предоставляет информацию о пользователе и проверяет подписку.
    """
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('id', 'username',
                  'first_name', 'last_name',
                  'email', 'avatar', 'is_subscribed'
                  )

    def get_is_subscribed(self, obj):
        user = self.context.get('request').user
        if user.is_authenticated:
            return obj.followers.filter(user=user).exists()
        return False


class UserRegisterSerializer(serializers.ModelSerializer):
    """Сериализатор регистрации пользователя.
       Обрабатывает регистрацию нового пользователя,
       включая валидацию имени пользователя и хэширование пароля.
    """
    password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ('id', 'username',
                  'first_name', 'last_name',
                  'email', 'password'
                  )

    def validate_username(self, value):
        if not re.match(r'^[\w.@+-]+$', value):
            raise serializers.ValidationError(
                'Недопустимые символы в имени пользователя.'
            )
        return value

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user


class SubscripSerializer(serializers.ModelSerializer):
    """Сериализатор подписки
       Обрабатывает подписку пользователя на другого пользователя,
       включая валидацию уникальности подписок.
    """
    user = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        default=serializers.CurrentUserDefault()
    )
    cooker = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())

    class Meta:
        model = Subscription
        fields = ('id', 'user', 'cooker')
        validators = (
            UniqueTogetherValidator(
                queryset=Subscription.objects.all(),
                fields=('user', 'cooker'),
                message='Вы уже подписаны на этого пользователя'
            ),
        )

    def validate_cooker(self, value):
        if self.context['request'].user == value:
            raise serializers.ValidationError(
                'Нельзя подписываться на самого себя')
        return value


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор ингредиента
       Представляет информацию об ингредиенте,
       включая его имя и единицу измерения.
    """
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор тега
       Представляет информацию о теге, включая его имя и (уникальный)слаг.
    """
    class Meta:
        model = Tag
        fields = ('id', 'name', 'slug')


class RecipeIngredientReadSerializer(serializers.ModelSerializer):
    """Сериализатор для чтения ингредиентов рецепта.

    Обрабатывает сериализацию ингредиентов рецепта, включая
    их идентификаторы, имена, единицы измерения и количество.
"""
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit')
    amount = serializers.IntegerField()

    class Meta:
        model = IngredientRecipe
        fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipeIngredientWriteSerializer(serializers.ModelSerializer):
    """Сериализатор для записи ингредиентов в рецепт.

    Обрабатывает сериализацию данных о количестве
    и идентификаторах ингредиентов.
    """
    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all(),
    )

    class Meta:
        model = IngredientRecipe
        fields = ('id', 'amount')


class RecipeReadSerializer(serializers.ModelSerializer):
    """Сериализатор для чтения рецептов.

    Обрабатывает сериализацию данных рецепта, включая информацию об
    авторе, тегах, ингредиентах и статусах "в избранном" и "в корзине".
    """

    author = UserSerializer()
    tags = TagSerializer(many=True)
    ingredients = RecipeIngredientReadSerializer(
        many=True, source='recipe_ingredients',
    )
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            'id', 'author', 'tags', 'name', 'image', 'text',
            'ingredients', 'is_favorited',
            'is_in_shopping_cart', 'cooking_time',
        )
        read_only_fields = ('author', 'tags', 'ingredients',)

    def get_is_favorited(self, obj):
        """Определяет, находится ли рецепт
           в избранном для текущего пользователя.

        Аргументы:
            obj: Экземпляр рецепта, для которого проверяется статус.

        Возвращает:
            bool: True, если рецепт в избранном, иначе False.
        """
        user = self.context.get('request').user
        if user.is_authenticated:
            return obj.favorites.filter(user=user).exists()
        return False

    def get_is_in_shopping_cart(self, obj):
        """Определяет, находится ли рецепт в корзине для текущего пользователя.
        Аргументы:
            obj: Экземпляр рецепта, для которого проверяется статус.

        Возвращает:
            bool: True, если рецепт в корзине, иначе False.
        """
        user = self.context.get('request').user
        if user.is_authenticated:
            return obj.cart_set.filter(user=user).exists()
        return False


class ShortRecipeSerializer(RecipeReadSerializer):
    """Сериализатор для краткой информации о рецептах.

    Обрабатывает сериализацию основных данных рецепта, включая
    название, изображение и время приготовления.
    """

    image = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')

    def get_image(self, obj):
        """Получает URL для изображения рецепта.

        Аргументы:
            obj: Экземпляр рецепта, для которого извлекается изображение.

        Возвращает:
            str: URL к изображению
            или None, если изображение отсутствует.
        """
        request = self.context.get('request')
        if obj.image:
            return request.build_absolute_uri(obj.image.url)
        return None


class RecipeCreateUpdateSerializer(serializers.ModelSerializer):
    """
    Сериализатор для создания и обновления рецептов.

    Обрабатывает сериализацию данных рецепта,
    включая ингредиенты, теги, изображение,
    название, текст и время приготовления.
    Поддерживает валидацию тегов и ингредиентов.
    """
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(), many=True, required=True
    )
    ingredients = RecipeIngredientWriteSerializer(
        source='recipe_ingredients', many=True, required=True
    )
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = ('ingredients', 'tags', 'image', 'name', 'text',
                  'cooking_time')

    def create_recipe_igredient(self, recipe, ingredients_data):
        """
        Создает связанные объекты ингредиентов для заданного рецепта.

        Аргументы:
            recipe: Экземпляр рецепта, к которому будут привязаны ингредиенты.
            ingredients_data: Данные о ингредиентах для записи.
        """
        recipe_ingredient_objs = [
            IngredientRecipe(
                recipe=recipe,
                ingredient=ingredient_data['id'],
                amount=ingredient_data['amount']
            ) for ingredient_data in ingredients_data
        ]
        IngredientRecipe.objects.bulk_create(recipe_ingredient_objs)

    def create(self, validated_data):
        """
        Создает новый экземпляр рецепта с заданными данными.

        Аргументы:
            validated_data: Валидированные данные о рецепте.

        Возвращает:
            Экземпляр созданного рецепта.
        """
        ingredients_data = validated_data.pop('recipe_ingredients')
        recipe = super().create(validated_data)
        self.create_recipe_igredient(recipe, ingredients_data)
        return recipe

    def update(self, instance, validated_data):
        """
        Обновляет существующий экземпляр рецепта с заданными данными.

        Аргументы:
            instance: Экземпляр рецепта, который необходимо обновить.
            validated_data: Валидированные данные для обновления.

        Возвращает:
            Обновленный экземпляр рецепта.
        """
        ingredients_data = validated_data.pop('recipe_ingredients')
        instance = super().update(instance, validated_data)
        instance.recipe_ingredients.all().delete()
        self.create_recipe_igredient(instance, ingredients_data)
        return instance

    def validate_tags(self, value):
        """
        Проверяет корректность тегов.

        Аргументы:
            value: Список тегов для валидации.

        Возвращает:
            Отфильтрованные теги.

        Исключения:
            serializers.ValidationError: Если список тегов пуст
            или содержит дубликаты.
        """
        if not value:
            raise serializers.ValidationError(
                'Поле не может быть пустым.'
            )
        unique_tags = {tag.id for tag in value}
        if len(value) != len(unique_tags):
            raise serializers.ValidationError(
                'Теги не должны повторяться'
            )
        return value

    def validate_ingredients(self, value):
        """
        Проверяет корректность ингредиентов.

        Аргументы:
            value: Список ингредиентов для валидации.

        Возвращает:
            Отфильтрованные ингредиенты.

        Исключения:
            serializers.ValidationError: Если список ингредиентов пуст
            или содержит дубликаты.
        """
        if not value:
            raise serializers.ValidationError(
                'Поле не может быть пустым.'
            )
        unique_ingredients = {ing['id'].id for ing in value}
        if len(value) != len(unique_ingredients):
            raise serializers.ValidationError(
                'Ингредиенты не должны повторяться.'
            )
        return value

    def validate(self, data):
        """
        Проверяет наличие обязательных полей.

        Аргументы:
            data: Данные для валидации.

        Возвращает:
            Отфильтрованные данные.

        Исключения:
            serializers.ValidationError: Если отсутствуют обязательные поля.
        """
        required_fields = (
            'tags', 'recipe_ingredients', 'name', 'text', 'cooking_time'
        )
        missing_fields = [
            field for field in required_fields if field not in data
        ]
        if missing_fields:
            raise serializers.ValidationError(
                f"Отсутствуют обязательные поля: {', '.join(missing_fields)}"
            )
        return data

    def to_representation(self, instance):
        """
        Преобразует экземпляр рецепта в формат для чтения.

        Аргументы:
            instance: Экземпляр рецепта.

        Возвращает:
            Сериализованные данные рецепта.
        """
        return RecipeReadSerializer(
            instance, context=self.context
        ).data


class RecipesForUser(UserSerializer):
    """
    Сериализатор для представления пользователя с его рецептами.

    Обрабатывает дополнительно информацию о рецептах пользователя, включая
    их количество и список рецептов с учетом ограничения на количество.
    """
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.IntegerField(read_only=True, default=0)

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name', 'last_name',
                  'is_subscribed', 'recipes', 'recipes_count', 'avatar')

    def get_recipes(self, obj):
        """
        Получает список рецептов пользователя с учетом лимита.

        Аргументы:
            obj: Экземпляр пользователя.

        Возвращает:
            Список сериализованных рецептов.
        """
        request = self.context.get('request')
        recipes = obj.recipes.all()
        try:
            limit = int(request.query_params.get('recipes_limit'))
            recipes = recipes[:limit]
        except TypeError:
            pass
        return ShortRecipeSerializer(recipes, many=True,
                                     context={'request': request}).data


class UserRecipeCreationSerializer(serializers.ModelSerializer):
    """
    Сериализатор для создания связи между пользователем и рецептом.

    Обрабатывает валидацию на уникальность пары (пользователь, рецепт)
    для предотвращения дублирования записей.
    """

    class Meta:
        model = None
        fields = ('user', 'recipe')

    def __init__(self, *args, **kwargs):
        """
        Инициализирует сериализатор и устанавливает модель, если она передана.

        Аргументы:
            *args: Позиционные аргументы для родительского класса.
            **kwargs: Ключевые аргументы для настройки сериализатора.
                Включает 'model_class', которая используется для настройки
                класса модели и ее валидаторов.

        """
        model_class = kwargs.pop('model_class', None)
        if model_class:
            self.Meta.model = model_class
            self.Meta.validators = (
                UniqueTogetherValidator(
                    queryset=model_class.objects.all(),
                    fields=('user', 'recipe'),
                    message=(
                        'Рецепт уже добавлен в '
                        f'{model_class._meta.verbose_name}.'
                    )
                ),
            )
        super().__init__(*args, **kwargs)

    def to_representation(self, instance):
        """
        Преобразует экземпляр отношения пользователя и рецепта
        в формат для чтения.

        Аргументы:
            instance: Экземпляр отношения, который нужно сериализовать.

        Возвращает:
            dict: Сериализованные данные рецепта.
        """
        recipe = instance.recipe
        return ShortRecipeSerializer(recipe, context=self.context).data
