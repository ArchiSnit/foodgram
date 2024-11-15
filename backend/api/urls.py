from django.urls import include, path
from rest_framework.routers import DefaultRouter

from api.views import (
    UserViewSet,
    RecipeViewSet,
    TagViewSet,
    IngredientViewSet,
)

api_v1 = DefaultRouter()
api_v1.register(r'users', UserViewSet, basename='users')
api_v1.register(r'tags', TagViewSet)
api_v1.register(r'ingredients', IngredientViewSet)
api_v1.register(r'recipes', RecipeViewSet)


urlpatterns = [
    path('', include(api_v1.urls)),
    path('auth/', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
]
