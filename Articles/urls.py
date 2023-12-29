# articles_igl_engine/core/urls.py
from django.urls import path, re_path
from .views import display_favorite_articles, add_to_favorite, remove_favorite
from Users.views import login

urlpatterns = [
    path('', display_favorite_articles, name='display_favorite_articles'),
    path('add_to_favorite/<str:article_id>', add_to_favorite, name='add_to_favorite'),
    path('remove/<str:article_id>', remove_favorite, name='remove_favorite')
]
