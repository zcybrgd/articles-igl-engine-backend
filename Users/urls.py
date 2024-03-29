from django.urls import re_path, path
from . import views
from .views import userSettings, modManipulation, adminStats

urlpatterns = [
    re_path('signup', views.signup),
    re_path('login', views.login),
    path('client/<int:id>', views.client_login),#view to get the info of the currently connected client
    path('client/modify', views.modify_client), #view to modify the info of the currently connected client
    path('mod/add', modManipulation.add_mod),  # the view to add a mod
    path('mod/modify/<int:id>', modManipulation.modify_mod),  # view to modify a mod using its id
    path('mod/delete/<int:id>', modManipulation.delete_mod),  # view to delete a mod using its id
    path('mods/display', modManipulation.display_mods),  # view to display the mods of the admin currently connected
    path('mods/added', adminStats.added_mods),  # returns the number of mods added by the admin connected
    path('mods/total', adminStats.total_mods),  # returns the total number of mods
    path('mods/deleted', adminStats.deleted_mods),  # returns the number of mods the admin has deleted
    path('articles/deleted', adminStats.deleted_articles),  # returns the number of articles the admin connected's mods have deleted
    path('articles/validated', adminStats.validated_articles),  # returns the number of articles the admin connected's mods have validated
    path('articles/modified', adminStats.modified_articles),  # returns the number of edits the admin connected's mods have done on the articles
    path('contactInfo/', views.contactInfo),  # AddContactInfo
    path('Displaycontacts/', views.contactsMsgs),  # View all the Contacts Information
    path('changeSettings/client/<int:id>', userSettings.modifyClient),  # Change settings info for a client
]
