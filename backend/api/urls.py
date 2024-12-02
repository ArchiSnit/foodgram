from django.urls import include, path
from rest_framework.routers import DefaultRouter


from api.views import (
    TagViewSet,
    UserViewSet,
    RecipeViewSet,
    IngredientViewSet,
)

api_v1 = DefaultRouter()
api_v1.register('tags', TagViewSet, basename='tag')
api_v1.register('users', UserViewSet, basename='user')
api_v1.register('recipes', RecipeViewSet, basename='recipe')
api_v1.register('ingredients', IngredientViewSet, basename='ingredient')


urlpatterns = [
    path('', include(api_v1.urls)),
    # path('auth/', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
]
