from django.urls import re_path, path
from . import views
from .views import users_list, clients_list, delete_user, delete_client, mods_list, admins_list, modManipulation, adminStats, delete_everything

urlpatterns = [
    re_path('signup', views.signup),
    re_path('login', views.login),
    path('users', users_list),  # view to all the users
    path('user/<int:id>', delete_user),  # view to delete a user using its id
    path('client/<int:id>', delete_client),  # delete a client using its id
    path('clients', clients_list),  # view to all the clients
    path('mods', mods_list),  # view to all the mods
    path('admins', admins_list),  # view to all the admins
    path('mod/add', modManipulation.add_mod),  # the view to add a mod
    path('mod/modify/<int:id>', modManipulation.modify_mod),  # view to modify a mod using its id
    path('mod/delete/<int:id>', modManipulation.delete_mod),  # view to delete a mod using its id
    path('mod/deleteeverything',delete_everything),
    path('mods/display', modManipulation.display_mods),  # view to display the mods of the admin currently connected
    path('mods/added', adminStats.added_mods),  # returns the number of mods added by the admin connected
    path('mods/total', adminStats.total_mods),  # returns the total number of mods
    path('mods/deleted', adminStats.deleted_mods),  # returns the number of mods the admin has deleted
    path('articles/deleted', adminStats.deleted_articles),  # returns the number of articles the admin connected's mods have deleted
    path('articles/validated', adminStats.validated_articles),  # returns the number of articles the admin connected's mods have validated
    path('articles/modified', adminStats.modified_articles),  # returns the number of edits the admin connected's mods have done on the articles
]
