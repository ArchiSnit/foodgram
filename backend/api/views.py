import short_url

from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.filters import SearchFilter
from django.shortcuts import redirect, get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, mixins, status, serializers
from rest_framework.permissions import (IsAuthenticated, AllowAny,
                                        IsAuthenticatedOrReadOnly
                                        )
from api.permissions import OwnerOnly, IsAuthorOrReadOnly
from api.serializers import (UserGetSerializer, UserPostSerializer,
                             Base64ImageField, Subscription,
                             SubscriptionListSerializer,
                             SubscriptionSerializer, TagSerializer,
                             IngredientSerializer, RecipeCreateSerializer,
                             RecipeSerializer, FavoriteRecipeSerializer,
                             ShoppingCartSerializer
                             )


from users.models import (User, Subscription)

from recipes.models import (Tag, Ingredient, Recipe,
                            FavoriteRecipe, ShoppingCart
                            )


# def short_link_view(request, s):
#     """Редирект по короткой ссылке"""
#     try:
#         pk = decode_url(s)  # Декодируем короткую ссылку в ID рецепта
#     except (ValueError, TypeError):
#         raise Http404("Неверная короткая ссылка")
#
#     # Проверяем существование рецепта с указанным ID
#     if not Recipe.objects.filter(pk=pk).exists():
#         raise Http404("Рецепт не найден")
#
#     return redirect(f'/recipes/{pk}/')
#


def short_link_view(request, s):
    """Redirect для короткой ссылки"""
    pk = short_url.decode_url(s)
    return redirect(f'/recipes/{pk}/')


class UserViewSet(viewsets.ModelViewSet):
    """ViewSet для работы с пользователями."""
    queryset = User.objects.all()
    permission_classes = [AllowAny]

    def get_permissions(self):
        """Определяем доступ к методам."""
        if self.action in ['retrieve', 'me']:
            return [IsAuthenticated()]
        return super().get_permissions()

    def get_serializer_class(self):
        """Определяем сериализатор в зависимости от действия."""
        if self.action == 'create':
            return UserPostSerializer
        return UserGetSerializer

    @action(detail=False, methods=['get'],
            permission_classes=[IsAuthenticated]
            )
    def me(self, request):
        """Эндпоинт для получения информации о текущем пользователе."""
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)

    @action(detail=False, methods=['patch'],
            permission_classes=[IsAuthenticated]
            )
    def update_avatar(self, request):
        """Метод для добавления или обновления аватара."""
        user = request.user
        serializer = Base64ImageField()
        try:
            avatar = serializer.to_internal_value(request.data.get('avatar'))
            user.avatar = avatar
            user.save()
            return Response({'detail': 'Аватар обновлен.'},
                            status=status.HTTP_200_OK)

        except serializers.ValidationError as avatar_error:
            return Response({'detail': str(avatar_error)},
                            status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['delete'],
            permission_classes=[IsAuthenticated]
            )
    def delete_avatar(self, request):
        """Метод для удаления аватара."""

        user = request.user
        if user.avatar:
            user.avatar.delete(save=True)
            return Response({'detail': 'Аватар удален.'},
                            status=status.HTTP_200_OK)

        return Response({'detail': 'У пользователя нет аватара.'},
                        status=status.HTTP_400_BAD_REQUEST)


class SubscriptionViewSet(viewsets.GenericViewSet,
                          mixins.ListModelMixin,
                          mixins.CreateModelMixin):
    """ViewSet для работы с подписками."""
    serializer_class = SubscriptionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Возвращает подписки текущего пользователя."""
        return Subscription.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        """Устанавливает текущего пользователя как автора подписки."""
        serializer.save(user=self.request.user)

    @action(detail=False, methods=['get'])
    def my_subscriptions(self, request):
        """Эндпоинт для получения списка подписок текущего пользователя."""
        subscriptions = Subscription.objects.filter(user=request.user)
        serializer = SubscriptionListSerializer(subscriptions, many=True)
        return Response(serializer.data)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet для чтения тегов."""
    queryset = Tag.objects.all()
    permission_classes = (OwnerOnly,)
    serializer_class = TagSerializer


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet для чтения ингредиентов."""
    queryset = Ingredient.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = IngredientSerializer
    filter_backends = (DjangoFilterBackend, SearchFilter)
    search_fields = ('^name',)


class RecipeViewSet(viewsets.ModelViewSet):
    """ViewSet для управления рецептами."""
    queryset = Recipe.objects.all()
    permission_classes = [IsAuthenticatedOrReadOnly, IsAuthorOrReadOnly]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['tags', 'author']

    def get_serializer_class(self):
        """Определяет сериализатор в зависимости от действия."""
        if self.action in ['create', 'update', 'partial_update']:
            return RecipeCreateSerializer
        return RecipeSerializer

    def perform_create(self, serializer):
        """
        Устанавливает текущего пользователя как автора при создании рецепта.
        """
        serializer.save(author=self.request.user)

    @action(detail=True, methods=['post', 'delete'],
            permission_classes=[IsAuthenticated])
    def favorite(self, request, pk=None):
        """Добавление/удаление рецепта в/из избранного."""
        recipe = self.get_object()
        if request.method == 'POST':
            serializer = FavoriteRecipeSerializer(
                data={'user': request.user.id, 'recipe': recipe.id})
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(
                {'status': 'Рецепт добавлен в избранное'}, status=201)
        if request.method == 'DELETE':
            FavoriteRecipe.objects.filter(
                user=request.user, recipe=recipe).delete()
            return Response(
                {'status': 'Рецепт удалён из избранного'}, status=204)

    @action(detail=True, methods=['post', 'delete'],
            permission_classes=[IsAuthenticated])
    def shopping_cart(self, request, pk=None):
        """Добавление/удаление рецепта в/из корзины."""
        recipe = self.get_object()

        if request.method == 'POST':
            serializer = ShoppingCartSerializer(
                data={'user': request.user.id, 'recipe': recipe.id})
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(
                {'status': 'Рецепт добавлен в корзину'}, status=201)

        if request.method == 'DELETE':
            ShoppingCart.objects.filter(
                user=request.user, recipe=recipe).delete()

            return Response(
                {'status': 'Рецепт удалён из корзины'}, status=204)

    @action(detail=True, methods=['get'],
            permission_classes=[IsAuthenticatedOrReadOnly])
    def short_link(self, request, pk=None):
        """Возвращает короткую ссылку на рецепт."""
        recipe = get_object_or_404(Recipe, pk=pk)
        short_id = short_url.encode_url(recipe.id)
        return Response(
            {'short_link': f'{request.build_absolute_uri("/")}{short_id}/'})
