from django.urls import path
from .views import users_list, delete_user, delete_mod, admin_list
from .views import mods_list

urlpatterns = [
    path('mods', mods_list),#or ^mods/$
    path('users', users_list),
    path('admins', admin_list),
    path('users/<int:id>', delete_user),
    path('mod/delete/<int:id>', delete_mod),
]
