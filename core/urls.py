from django.urls import path, include
from .views import home

urlpatterns = [
path('', home, name='home'),
]
