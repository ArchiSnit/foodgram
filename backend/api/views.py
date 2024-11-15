import short_url

from django.http import HttpResponse
from django.conf import settings
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404, redirect
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet as UVS
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import (AllowAny, IsAuthenticated)
from rest_framework.response import Response

from api.filters import IngredientFilter, RecipeFilter
from api.paginators import LimitPageNumberPaginator
from api.permissions import OwnerOnly
from api.serializers import (
    IngredientSerializer,
    RecipeGetSerializer,
    RecipePostSerializer,
    SubscriptionSerializer,
    TagSerializer,
    UserGetSerializer,
    UserRecepieSerializer,
    UserSubscriptionsSerializer,
)
from recipes.models import (
    FavoriteRecipe,
    Ingredient,
    Recipe,
    RecipeIngredient,
    ShopRecipe,
    Subscription,
    Tag
)

User = get_user_model()


def redirect_view(request, s):
    """Redirect для короткой ссылки"""
    pk = short_url.decode_url(s)
    return redirect(f'/recipes/{pk}/')


class UserViewSet(UVS):
    """
    Вьюсет для управления пользователями.
    Предоставляет методы для получения информации о пользователе,
    а также для работы с аватаром и подписками.
    """
    queryset = User.objects.all()
    pagination_class = LimitPageNumberPaginator

    @action(detail=False, methods=('get',),
            permission_classes=(IsAuthenticated,))
    def me(self, request):
        """Получение информации о текущем пользователе."""
        serializer = UserGetSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, url_path=r'me/avatar',
            permission_classes=(IsAuthenticated,))
    def avatar(self, request):
        """Получение или изменение аватара пользователя."""
        if request.method == 'GET':
            # Получить аватар текущего пользователя
            serializer = UserGetSerializer(request.user)
            return Response({'avatar': serializer.data.get('avatar')})

        elif request.method == 'PUT':
            # Изменить аватар текущего пользователя
            serializer = UserGetSerializer(request.user,
                                           data=request.data,
                                           partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response({'avatar': serializer.data.get('avatar')})

    @avatar.mapping.put
    def set_avatar(self, request):
        """Установка аватара для текущего пользователя."""
        user = get_object_or_404(User, pk=request.user.id)
        serializer = UserGetSerializer(
            user, data=request.data, partial=True,
            context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'avatar': serializer.data.get('avatar')})

    @avatar.mapping.delete
    def delete_avatar(self, request):
        """Удаление аватара у текущего пользователя."""
        User.objects.filter(pk=request.user.id).update(avatar=None)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, permission_classes=(IsAuthenticated,))
    def subscriptions(self, request):
        """Получение списка подписок текущего пользователя."""
        users = User.objects.filter(followers__user=request.user)
        limit_param = request.query_params.get('recipes_limit')
        paginated_queryset = self.paginate_queryset(users)
        serializer = UserSubscriptionsSerializer(
            paginated_queryset,
            context={
                'limit_param': limit_param},
            many=True)
        return self.get_paginated_response(serializer.data)

    @action(detail=True,
            permission_classes=(IsAuthenticated,))
    def subscribe(self, request, id):
        """Подписка на пользователя с указанным ID."""

    @subscribe.mapping.post
    def create_subs(self, request, id):
        """Создание подписки на пользователя с указанным ID."""
        limit_param = request.query_params.get('recipes_limit')
        serializer = SubscriptionSerializer(
            data=request.data,
            # передача контекста для валидации
            context={
                'request': request,
                'user_pk': id,
                'limit_param': limit_param,
                'action': 'create_subs'})
        serializer.is_valid(raise_exception=True)
        subs = serializer.save(pk=id)
        return Response(subs.data, status=status.HTTP_201_CREATED)

    @subscribe.mapping.delete
    def delete_subs(self, request, id):
        """Удаление подписки на пользователя с указанным ID."""
        serializer = SubscriptionSerializer(
            data=request.data,
            # передача контекста для валидации
            context={
                'request': request,
                'user_pk': id,
                'action': 'delete_subs'})
        serializer.is_valid(raise_exception=True)
        get_object_or_404(
            Subscription,
            user=self.request.user,
            cooker=get_object_or_404(User, pk=id)).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """Для тегов"""
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None
    permission_classes = (AllowAny,)


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """Для ингредиентов"""
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None
    permission_classes = (AllowAny,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientFilter


class RecipeViewSet(viewsets.ModelViewSet):
    """Вьюсет для работы с рецептами.

    Позволяет получать, добавлять, редактировать и удалять рецепты.
    Включает возможность добавления рецептов в избранное и корзину покупок.
    """
    queryset = Recipe.objects.all()
    permission_classes = (IsAuthenticated, OwnerOnly)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter
    pagination_class = LimitPageNumberPaginator

    def get_permissions(self):
        """Определяет права доступа в зависимости от действия.

        Позволяет всем пользователям получать список рецептов,
        детали рецепта и короткую ссылку на рецепт.
        Остальные действия требуют аутентификации.
        """
        if self.action in ('list', 'retrieve', 'get_link'):
            return (AllowAny(),)
        return (IsAuthenticated(), OwnerOnly())

    def get_serializer_class(self):
        """Определяет используемый сериализатор в зависимости от действия.

        Использует RecipeGetSerializer для получения данных
        о рецептах, а RecipePostSerializer для добавления и обновления.
        """
        if self.action in ('list', 'retrieve'):
            return RecipeGetSerializer
        return RecipePostSerializer

    @action(detail=True, permission_classes=(IsAuthenticated,))
    def favorite(self, request, pk):
        """Промежуточный метод, для определения в дальнейшем"""

    @favorite.mapping.post
    def add_into_fav(self, request, pk):
        """Добавляет рецепт в избранное.
        Проверяет данные, переданные с запросом,
        и сохраняет рецепт в избранное.
        Возвращает данные о любимом рецепте при успехе
        и ошибку при неудаче."""
        serializer = UserRecepieSerializer(
            data=request.data,
            #  передача контекста для валидации
            context={
                'request': request,
                'recipe_pk': pk,
                'action': 'add',
                'model': FavoriteRecipe})
        serializer.is_valid(raise_exception=True)
        short_recipe = serializer.save(pk=pk)
        return Response(short_recipe.data, status=status.HTTP_201_CREATED)

    @favorite.mapping.delete
    def del_from_fav(self, request, pk):
        """Удаляет рецепт из избранного.

        Проверяет данные, переданные с запросом,
        и удаляет рецепт из избранного.
        Возвращает ответ без содержимого при успешном удалении.
        """
        serializer = UserRecepieSerializer(
            data=request.data,
            #  передача контекста для валидации
            context={
                'request': request,
                'recipe_pk': pk,
                'action': 'del',
                'model': FavoriteRecipe})
        serializer.is_valid(raise_exception=True)
        get_object_or_404(
            FavoriteRecipe,
            user=self.request.user,
            recipe=get_object_or_404(Recipe, pk=pk)).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, permission_classes=(AllowAny,), url_path='get-link')
    def get_link(self, request, pk):
        """Генерирует короткую ссылку на рецепт.

        Возвращает URL-адрес для быстрого доступа к рецепту
        по короткой ссылке.
        """
        url = 'http://{}/s/{}/'.format(
            settings.ALLOWED_HOSTS[0],
            short_url.encode_url(int(pk))
        )
        return Response({'short-link': url}, status=status.HTTP_200_OK)

    @action(detail=True, permission_classes=(IsAuthenticated,))
    def shopping_cart(self, request, pk):
        """Добавляет или удаляет рецепт из корзины покупок.

        Используется метод POST для добавления рецепта в корзину
        и DELETE для удаления из корзины.
        """

    @shopping_cart.mapping.post
    def add_into_cart(self, request, pk):
        """Добавляет рецепт в корзину покупок.

        Проверяет данные, переданные с запросом, и сохраняет рецепт.
        Возвращает данные о рецепте при успехе и ошибку при неудаче.
        """
        serializer = UserRecepieSerializer(
            data=request.data,
            #  передача контекста для валидации
            context={
                'request': request,
                'recipe_pk': pk,
                'action': 'add',
                'model': ShopRecipe})
        serializer.is_valid(raise_exception=True)
        short_recipe = serializer.save(pk=pk)
        return Response(short_recipe.data, status=status.HTTP_201_CREATED)

    @shopping_cart.mapping.delete
    def del_from_cart(self, request, pk):
        """Удаляет рецепт из корзины покупок.

        Проверяет данные, переданные с запросом, и удаляет рецепт из корзины.
        Возвращает ответ без содержимого при успешном удалении.
        """
        serializer = UserRecepieSerializer(
            data=request.data,
            #  передача контекста для валидации
            context={
                'request': request,
                'recipe_pk': pk,
                'action': 'del',
                'model': ShopRecipe})
        serializer.is_valid(raise_exception=True)
        get_object_or_404(
            ShopRecipe,
            user=self.request.user,
            recipe=get_object_or_404(Recipe, pk=pk)).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, permission_classes=(IsAuthenticated,))
    def download_shopping_cart(self, request):
        """Скачивает список покупок для рецептов в корзине.

        Возвращает текстовый файл с ингредиентами всех рецептов,
        находящихся в корзине пользователя.
        """
        user = request.user
        if user.is_anonymous:
            return Response(
                {'message': 'Вы должны быть авторизованы, '
                 'чтобы скачать список покупок. '
                 'Пожалуйста, выполните вход в свою учетную запись.'})

        recipe_ingredients = RecipeIngredient.objects.filter(
            recipe_id__in=user.shops.values('recipe_id'))
        ingredients = {}
        for recipe_ingredient in recipe_ingredients:
            ingredients.setdefault(
                recipe_ingredient.ingredient, []
            ).append(recipe_ingredient.amount)
        text, count = '', 0
        for item in ingredients:
            count += 1
            text += (
                f'{count}. {item.name} - '
                f'{sum(ingredients[item])} '
                f'{item.measurement_unit} \n')
        response = HttpResponse(text, content_type='text/plain; charset=UTF-8')
        response['Content-Disposition'] = 'attachment; filename="shops.txt"'
        return response
