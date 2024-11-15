import base64
from django.db.models import F

from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile

from django.shortcuts import get_list_or_404, get_object_or_404
from djoser.serializers import UserCreateSerializer, UserSerializer
from rest_framework import serializers

from users.constants import (
    MAX_AMOUNT,
    MAX_COOKING,
    MIN_AMOUNT,
    MIN_COOKING
)
from recipes.models import (
    FavoriteRecipe,
    Ingredient,
    Recipe,
    RecipeIngredient,
    RecipeTag,
    ShopRecipe,
    Subscription,
    Tag
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


class UserPostSerializer(UserCreateSerializer):
    """
    ТОЛЬКО для создания пользователя.
    Унаследован от djoser, чтобы взять пароль, токен итд.
    """

    class Meta(UserCreateSerializer.Meta):
        model = User
        fields = (
            'email', 'id',
            'username', 'first_name',
            'last_name', 'password'
        )


class UserGetSerializer(UserSerializer):
    """Сериализатор для получения данных о пользователе."""
    is_subscribed = serializers.SerializerMethodField()
    avatar = Base64ImageField(required=False, allow_null=True)

    class Meta:
        model = User
        fields = (
            'email', 'id', 'username', 'first_name',
            'last_name', 'is_subscribed', 'avatar')

    def validate(self, data):
        """Валидация данных перед сохранением."""
        if request := self.context.get('request'):
            if request.method == 'PUT' and not data:
                raise serializers.ValidationError('Выберите фото')
        return data

    def get_is_subscribed(self, obj):
        """Проверка, подписан ли текущий пользователь на пользователя."""
        if request := self.context.get('request'):
            if request.user.is_anonymous:
                return False
            return request.user.following.filter(cooker=obj).exists()
        return False


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор для тэгов."""
    class Meta:
        model = Tag
        fields = ('__all__')


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для ингредиентов."""
    class Meta:
        model = Ingredient
        fields = ('__all__')


class RecipeGetSerializer(serializers.ModelSerializer):
    """Сериализатор для получения представления рецепта.

    Предназначен для отображения информации о рецепте, включая
    автора, тэги, ингредиенты, а также информацию о том,
    добавлен ли рецепт в избранное и в корзину.
    """
    author = UserGetSerializer()
    tags = TagSerializer(
        many=True,
    )
    ingredients = serializers.SerializerMethodField()
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            'id', 'tags', 'author', 'ingredients',
            'is_favorited', 'is_in_shopping_cart',
            'name', 'image', 'text', 'cooking_time'
        )

    def get_ingredients(self, obj):
        """Получение списка ингредиентов рецепта."""
        recipe = obj
        ingredients = recipe.ingredients.values(
            'id',
            'name',
            'measurement_unit',
            amount=F('recipeingredient__amount')
        )
        return ingredients

    def get_is_recipe(self, obj, model):
        """Проверка, добавлен ли рецепт в указанную модель."""
        """(избранное или корзина)."""
        if request := self.context.get('request'):
            user = request.user
            if user.is_anonymous:
                return False
            # фильтр используется, потому что на входе функции может
            # быть любая модель, а значит related_name могут быть разными
            return model.objects.filter(
                user=user, recipe=obj).exists()
        return False

    def get_is_favorited(self, obj):
        return self.get_is_recipe(obj, FavoriteRecipe)

    def get_is_in_shopping_cart(self, obj):
        return self.get_is_recipe(obj, ShopRecipe)


class RecipeIngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для работы с ингредиентами рецепта.

    Позволяет сериализовать и десериализовать данные ингредиентов,
    включая их идентификатор и количество. Ингредиенты должны
    быть связаны с моделью Ingredient.
    """

    id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all())
    amount = serializers.IntegerField(
        write_only=True,
        min_value=MIN_AMOUNT,
        max_value=MAX_AMOUNT
    )

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'amount')


class RecipePostSerializer(serializers.ModelSerializer):
    """
    Сериализатор для создания и обновления рецептов.
    Позволяет валидировать и сериализовать данные рецептов, включая
    ингридиенты и тэги, а также взаимодействовать с моделью Recipe.
    """
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True,
        required=True,
        allow_null=False,
        allow_empty=False,
    )
    ingredients = RecipeIngredientSerializer(
        many=True,
        required=True,
        allow_null=False,
        allow_empty=False,)
    author = serializers.HiddenField(
        default=serializers.CurrentUserDefault())
    image = Base64ImageField(required=True, allow_null=False)
    name = serializers.CharField(required=True, max_length=256)
    cooking_time = serializers.IntegerField(
        max_value=MAX_COOKING, min_value=MIN_COOKING)

    class Meta:
        model = Recipe
        fields = (
            'ingredients', 'tags', 'image',
            'name', 'text', 'cooking_time',
            'author')

    def validate(self, data):
        """"Валидация данных на наличие обязательных полей"""
        if 'tags' not in data:
            raise serializers.ValidationError('Не указаны тэги.')
        if 'ingredients' not in data:
            raise serializers.ValidationError('Не указаны ингредиенты.')
        return data

    def validate_ingredients(self, data):
        """Валидация ингредиентов на уникальность и существование в БД"""
        ingredients_list = [item['id'].id for item in data]
        if len(ingredients_list) != len(set(ingredients_list)):
            raise serializers.ValidationError(
                'Ингредиенты должны быть уникальными.'
            )

        get_list_or_404(Ingredient, id__in=ingredients_list)
        return data

    def validate_tags(self, data):
        """Валидация тэгов на уникальность и существование в БД."""
        tags_list = [item.id for item in data]
        if len(tags_list) != len(set(tags_list)):
            raise serializers.ValidationError('Тэги должны быть уникальными.')
        get_list_or_404(Tag, id__in=tags_list)
        return data

    def add_tags_ingredients(self, recipe, tags, ingredients):
        """Добавляет теги и ингредиенты в рецепт"""
        RecipeTag.objects.bulk_create([
            RecipeTag(recipe=recipe, tag=tag) for tag in tags
        ])
        RecipeIngredient.objects.bulk_create([
            RecipeIngredient(
                recipe=recipe,
                ingredient=dict(ingredient).get('id'),
                amount=dict(ingredient).get('amount')
            ) for ingredient in ingredients
        ])

    def create(self, validated_data):
        """Создание нового рецепта."""
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(**validated_data)
        self.add_tags_ingredients(recipe, tags, ingredients)
        return recipe

    def update(self, instance, validated_data):
        """Обновление существующего рецепта."""
        # Очищаем текущие теги и ингредиенты
        instance.tags.clear()
        instance.ingredients.clear()

        instance.name = validated_data.get(
            'name', instance.name)
        instance.text = validated_data.get(
            'text', instance.text)
        instance.image = validated_data.get(
            'image', instance.image)
        instance.cooking_time = validated_data.get(
            'cooking_time', instance.cooking_time)

        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')

        self.add_tags_ingredients(instance, tags, ingredients)

        instance.save()
        return instance

    def to_representation(self, instance):
        """Сериализация объекта рецепта для представления."""
        return RecipeGetSerializer(instance).data


class RecipeListSerializer(serializers.ModelSerializer):
    """
    Сериализатор для представления списка рецептов.
    Позволяет сериализовать данные рецепта, включая
    его название, изображение и время приготовления.
    """
    image = Base64ImageField(required=True, allow_null=False)

    class Meta:
        model = Recipe
        fields = (
            'id',
            'name',
            'image',
            'cooking_time',
        )


class UserRecepieSerializer(serializers.Serializer):
    """Сериализатор для управления рецептами пользователя"""
    """(добавление/удаление)."""

    def validate(self, data):
        """
        Проверка данных на валидность перед добавлением или удалением рецепта.

        :param data: Данные рецепта, которые необходимо проверить.
        :return: Проверенные данные, если они валидны.
        :raises serializers.ValidationError: Если данные некорректны.
        """
        user = self.context['request'].user
        recipe_id = self.context.get('recipe_pk')
        # действие: удалить или добавить
        action = self.context.get('action')
        # целевая модель добавления
        model = self.context.get('model')
        recipe = get_object_or_404(Recipe, pk=recipe_id)

        if not recipe:
            raise serializers.ValidationError('Рецепт не найден.')
        userrecipe = model.objects.filter(user=user, recipe=recipe)

        if action == 'del':
            # Проверяем, существует ли рецепт для удаления
            if not userrecipe:
                raise serializers.ValidationError(
                    'Подписка на рецепт не найдена.')

        if action == 'add':
            # Проверяем, существует ли рецепт для добавления
            if userrecipe:
                raise serializers.ValidationError(
                    'Вы уже подписаны на этот рецепт.')

        return data

    def create(self, validated_data):
        """
        Создание новой записи о рецепте пользователя.

        :param validated_data: Проверенные данные записи о рецепте.
        :return: Сериализованные данные созданного рецепта.
        :raises: Создаст новый объект в модели, указанной в контексте.
        """
        model = self.context.get('model')
        recipe = get_object_or_404(Recipe, pk=validated_data.get('pk'))

        # Создаём новую запись о рецепте
        model.objects.create(
            user=self.context['request'].user,
            recipe=recipe
        )
        # Возвращаем сериализованные данные созданного рецепта
        return RecipeListSerializer(recipe)


class SubscriptionSerializer(serializers.Serializer):
    """Сериализатор для управления подписками пользователей."""

    def validate(self, data):
        """
        Проверка данных на валидность перед созданием или удалением подписки.

        :param data: Данные подписки, которые необходимо проверить.
        :return: Проверенные данные, если они валидны.
        :raises serializers.ValidationError: Если данные некорректны.
        """
        user = self.context['request'].user
        subs_id = self.context.get('user_pk')
        action = self.context.get('action')

        subs = get_object_or_404(User, pk=subs_id)
        if not subs:
            raise serializers.ValidationError(
                'Пользователь не найден.')

        if user == subs:
            raise serializers.ValidationError(
                'Нельзя подписаться на самого себя.')

        subscription = user.following.filter(cooker=subs)

        if action == 'delete_subs':
            if not subscription:
                raise serializers.ValidationError(
                    'Вы не подписаны на этого пользователя.')

        if action == 'create_subs':
            if subscription:
                raise serializers.ValidationError(
                    'Вы уже подписаны на этого пользователя.')

        return data

    def create(self, validated_data):
        """
        Создание новой подписки.

        :param validated_data: Проверенные данные подписки.
        :return: Сериализованные данные нового объекта подписки.
        :raises: Создаст новый объект Subscription.
        """
        limit_param = self.context.get('limit_param')
        # Извлекаем пользователя, на которого подписываемся
        subs = get_object_or_404(User, pk=validated_data.get('pk'))

        # Создаём новую подписку
        Subscription.objects.create(
            user=self.context['request'].user,
            cooker=subs
        )

        # Возвращаем сериализованные данные с учетом лимита
        return UserSubscriptionsSerializer(
            subs,
            context={'limit_param': limit_param}
        )


class UserSubscriptionsSerializer(serializers.ModelSerializer):
    """Сериализатор для отображения подписки: recipe и count_recepie"""
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()
    is_subscribed = serializers.BooleanField(default=True)

    class Meta:
        model = User
        fields = (
            'id',
            'username',
            'first_name',
            'last_name',
            'email',
            'is_subscribed',
            'avatar',
            'recipes_count',
            'recipes',
        )

    def get_recipes_count(self, obj):
        """
        Получить количество рецептов, связанных с пользователем.
        :param obj: Экземпляр пользователя (User).
        :return: Количество рецептов.
        """
        return obj.recipes.count()

    def get_recipes(self, obj):
        """
        Получить список рецептов пользователя с учетом лимита.

        :param obj: Экземпляр пользователя (User).
        :return: Сериализованные данные рецептов.
        """
        recipes = obj.recipes.all()
        if limit_param := self.context.get('limit_param'):
            recipes = recipes[:int(limit_param)]
        serializer = RecipeListSerializer(recipes, many=True, read_only=True)
        return serializer.data
