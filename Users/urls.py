from django.urls import re_path, path
from . import views
from .views import users_list, clients_list, delete_user, delete_client, mods_list, admins_list

urlpatterns = [
    re_path('signup', views.signup),
    re_path('login', views.login),
    path('users', users_list),
    path('clients', clients_list),
    path('mods', mods_list),
    path('admins', admins_list),
    path('users/<int:id>', delete_user),
    path('clients/<int:id>', delete_client),
]
