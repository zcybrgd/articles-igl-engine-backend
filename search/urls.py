# articles_igl_engine/core/urls.py
from django.urls import path
from .views import search_articles

urlpatterns = [
    path('nadi/', search_articles, name='search_articles'),
]
