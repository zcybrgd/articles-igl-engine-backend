from django.urls import path
from .views import home  # Import the home view

urlpatterns = [
    path('', home, name='home'),
]
