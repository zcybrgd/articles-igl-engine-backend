# articles_igl_engine/core/urls.py
from django.urls import path
from .views import FavoritesManipulation

urlpatterns = [
    path('', FavoritesManipulation.display_favorite_articles, name='display_favorite_articles'),
    path('add_to_favorite/<str:article_id>', FavoritesManipulation.add_to_favorite, name='add_to_favorite'),
    path('remove/<str:article_id>', FavoritesManipulation.remove_favorite, name='remove_favorite')
]
