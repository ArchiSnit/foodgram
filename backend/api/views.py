import short_url
from django.conf import settings
from django.db.models import Sum, Count, Prefetch
from djoser.serializers import SetPasswordSerializer

from rest_framework.response import Response
from rest_framework import viewsets, status
from rest_framework.decorators import action
from django.shortcuts import redirect, get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from api.permissions import IsAuthorOrReadOnly
from rest_framework.permissions import (AllowAny,
                                        IsAuthenticated,
                                        )
from api.serializers import (
    AvatarSerializer, IngredientSerializer, SubscribSerializer,
    RecipeCreateUpdateSerializer, RecipeReadSerializer,
    TagSerializer, UserRecipeCreationSerializer,
    UserRegisterSerializer, UserSerializer, RecipesForUser


)
from api.utils import create_shopping_list_pdf
from api.filters import RecipeFilter, IngredientFilter
from api.paginators import LimitPageNumberPaginator
from users.models import Subscribtion
from django.contrib.auth import get_user_model

from recipes.models import (Tag, Ingredient, Recipe,
                            IngredientRecipe,
                            FavoriteRecipe, ShoppingCart
                            )


User = get_user_model()


def short_link_view(request, s):
    """Redirect для короткой ссылки"""
    pk = short_url.decode_url(s)
    return redirect(f'/recipes/{pk}/')


class UserViewSet(viewsets.ModelViewSet):
    """
    ViewSet для работы с пользователями.

    Обрабатывает операции регистрации пользователя, изменения пароля,
    получения информации о текущем пользователе, управления аватаром
    и подписками на других пользователей.
    """
    queryset = User.objects.all()
    permission_classes = (AllowAny,)
    pagination_class = LimitPageNumberPaginator

    @action(['get'], detail=False, permission_classes=[IsAuthenticated])
    def me(self, request):
        """
        Получает информацию о текущем пользователе.
        """
        user = request.user
        serializer = UserSerializer(user, context={'request': request})
        return Response(serializer.data)

    @action(['post'], detail=False, permission_classes=[IsAuthenticated])
    def set_password(self, request):
        """
        Устанавливает новый пароль для текущего пользователя.
        Взято из Djoser - SetPasswordSerializer
        """
        serializer = SetPasswordSerializer(data=request.data,
                                           context={'request': request})
        serializer.is_valid(raise_exception=True)
        request.user.set_password(serializer.data['new_password'])
        request.user.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def get_serializer_class(self):
        """
        Определяет класс сериализатора в зависимости от метода запроса.

        """
        if self.request.method == 'POST':
            return UserRegisterSerializer
        return UserSerializer

    @action(['put', 'delete'], detail=False,
            permission_classes=[IsAuthenticated],
            url_path='me/avatar')
    def avatar(self, request):
        """
        Обрабатывает обновление или удаление аватара текущего пользователя.

        """
        user = self.request.user
        if request.method == 'PUT':
            serializer = AvatarSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            user.avatar = serializer.validated_data['avatar']
            user.save()
            avatar_url = request.build_absolute_uri(user.avatar.url)
            return Response({'avatar': avatar_url}, status=status.HTTP_200_OK)
        user.avatar.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(['get'], detail=False, permission_classes=[IsAuthenticated])
    def subscriptions(self, request):
        """
        Получает список подписок текущего пользователя.

        """
        user = request.user
        paginator = self.pagination_class()
        queryset = User.objects.filter(followers__user=user).annotate(
            recipe_count=Count('recipes')).order_by('-id')
        paginated_queryset = paginator.paginate_queryset(queryset, request)
        serializer = RecipesForUser(paginated_queryset, many=True,
                                    context={'request': request})
        return paginator.get_paginated_response(serializer.data)

    @action(['post'], detail=True, permission_classes=[IsAuthenticated])
    def subscribe(self, request, pk=None):
        """
        Подписывает текущего пользователя на другого пользователя.
        """
        user = request.user
        user_to_follow = get_object_or_404(User, id=pk)
        serializer = SubscribSerializer(
            data={'user': user.id, 'following': user_to_follow.id},
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        obj = User.objects.annotate(recipes_count=Count('recipes')).get(id=pk)
        response_serializer = RecipesForUser(obj,
                                             context={'request': request})
        return Response(response_serializer.data,
                        status=status.HTTP_201_CREATED)

    @subscribe.mapping.delete
    def delete_subscription(self, request, pk=None):
        """
        Отменяет подписку текущего пользователя на другого пользователя.
        """
        user = request.user
        user_to_unfollow = get_object_or_404(User, id=pk)

        subscribtion = Subscribtion.objects.filter(
            user=user, following=user_to_unfollow).first()

        if subscribtion:
            subscribtion.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

        return Response({'detail': 'Вы не подписаны на этого пользователя.'},
                        status=status.HTTP_400_BAD_REQUEST)


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet для ингредиентов"""
    queryset = Ingredient.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = IngredientSerializer
    filterset_class = IngredientFilter
    filter_backends = (DjangoFilterBackend,)
    pagination_class = None


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet для тегов"""
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (AllowAny,)
    pagination_class = None


class RecipeViewSet(viewsets.ModelViewSet):
    """Общий ViewSet рецептов"""
    queryset = Recipe.objects.prefetch_related(
        'tags',
        Prefetch(
            'recipe_ingredients',
            queryset=IngredientRecipe.objects.select_related('ingredient'))
    ).select_related('author')

    filterset_class = RecipeFilter
    http_method_names = ('get', 'post', 'patch', 'delete')
    # permission_classes = [IsAuthorOrReadOnly]
    pagination_class = LimitPageNumberPaginator

    def get_permissions(self):
        """Определяет разрешения в зависимости от метода запроса."""
        if self.action in ['list', 'retrieve']:
            return [AllowAny()]
        return [IsAuthorOrReadOnly()]

    def perform_create(self, serializer):
        """Добавление автора при создании рецепта."""
        self.object = serializer.save(author=self.request.user)

    def get_serializer_class(self):
        """Определение сериализатора в зависимости от метода запроса."""
        if self.request.method == 'GET':
            return RecipeReadSerializer
        return RecipeCreateUpdateSerializer

    @action(['get'], detail=False, permission_classes=[IsAuthenticated])
    def download_shopping_cart(self, request):
        """
        Скачивание списка покупок в формате PDF.
        Составляется на основе рецептов в корзине пользователя.
        """
        user = request.user
        ingredients_summary = user.cart_set.values(
            'recipe__ingredients__name',
            'recipe__ingredients__measurement_unit'
        ).annotate(total_amount=Sum('recipe__recipe_ingredients__amount'))
        return create_shopping_list_pdf(ingredients_summary)

    def create_user_recipe_creation(self, request, model, pk):
        """
        Универсальный метод для добавления рецепта в избранное или корзину.
        """
        user = request.user
        recipe = get_object_or_404(Recipe, id=pk)
        serializer = UserRecipeCreationSerializer(
            data={'user': user.id, 'recipe': recipe.id},
            model_class=model, context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete_user_recipe_creation(self, request, model, pk, error_msg=None):
        """
        Универсальный метод для удаления рецепта из избранного или корзины.
        """
        user = request.user
        recipe = get_object_or_404(Recipe, id=pk)
        if model.objects.filter(user=user, recipe=recipe).exists():
            model.objects.filter(user=user, recipe=recipe).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(error_msg, status=status.HTTP_400_BAD_REQUEST)

    @action(['post'], True, permission_classes=[IsAuthenticated],)
    def shopping_cart(self, request, pk=None):
        """Добавление рецепта в корзину."""
        return self.create_user_recipe_creation(request, ShoppingCart, pk)

    @shopping_cart.mapping.delete
    def delete_from_shopping_cart(self, request, pk=None):
        """Удаление рецепта из корзины."""
        if not request.user.is_authenticated:
            return Response(
                {
                    "detail": (
                        "Учетные данные для аутентификации не были "
                        "предоставлены.")
                },
                status=status.HTTP_401_UNAUTHORIZED)

        error_msg = 'Рецепт не был добавлен в корзину.'
        return self.delete_user_recipe_creation(request,
                                                ShoppingCart,
                                                pk, error_msg)

    @action(detail=False, methods=['get'],
            permission_classes=[IsAuthenticated])
    def favorite(self, request):
        """Список избранных рецептов текущего пользователя."""

        user = request.user
        queryset = Recipe.objects.filter(favorites__user=user).select_related(
            'author'
        ).prefetch_related('tags', 'recipe_ingredients__ingredient')

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = RecipeReadSerializer(page, many=True,
                                              context={'request': request})
            return self.get_paginated_response(serializer.data)

        serializer = RecipeReadSerializer(queryset, many=True,
                                          context={'request': request})
        return Response(serializer.data)

    @action(['post'], True, url_path='favorite',
            permission_classes=[IsAuthenticated],
            )
    def favorite_recipe(self, request, pk=None):
        """Добавление рецепта в избранное."""
        return self.create_user_recipe_creation(request, FavoriteRecipe, pk)

    @favorite_recipe.mapping.delete
    def delete_from_favorite(self, request, pk=None):
        """Удаление рецепта из избранного."""
        if not request.user.is_authenticated:
            return Response(
                {
                    "detail": (
                        "Учетные данные для аутентификации не были "
                        "предоставлены.")
                },
                status=status.HTTP_401_UNAUTHORIZED)

        error_msg = 'Рецепт не был добавлен в избранное.'
        return self.delete_user_recipe_creation(request,
                                                FavoriteRecipe,
                                                pk, error_msg
                                                )

    @action(['get'], True, permission_classes=[AllowAny],
            url_path='get-link')
    def get_link(self, request, pk=None):
        """
        Получение короткой ссылки,
        по первому значению в ALLOWED_HOSTS
        """
        url = 'http://{}/s/{}/'.format(
            settings.ALLOWED_HOSTS[0],
            short_url.encode_url(int(pk))
        )
        return Response({'short-link': url}, status=status.HTTP_200_OK)
