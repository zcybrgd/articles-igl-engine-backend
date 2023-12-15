from django.urls import path, include
from .admin import admin
from .views import add_mod, users_list, delete_user,  modify_mod, delete_mod, admin_list# Import the home view
from .views import mods_list

urlpatterns = [
    path('mods', mods_list),#or ^mods/$
    path('mods/add', add_mod),
    #path('signUp', signup),
    #path('login', login),
    path('users', users_list),
    path('admins', admin_list),
    path('users/<int:id>', delete_user),
   # path('admins', admins),
    path('mod/delete/<int:id>', delete_mod),
    path('mod/modify/<int:id>', modify_mod)
]
