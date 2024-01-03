
from django.urls import path
from .views import search_articles, total_articles, unreviewed_articles

urlpatterns = [
    path('nadi/', search_articles, name='search_articles'),
    path('', total_articles, name='total_articles'),
    path('unreviewed', unreviewed_articles, name='unreviewed_articles'),
]
