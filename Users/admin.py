from django.contrib import admin
from .models import Moderator


class WebsiteAdmin(admin.ModelAdmin):
    fields = ['userName', 'firstName', 'familyName', 'email', 'password', 'profile_picture','edit_count']
    list_display = ['userName', 'email']


admin.site.register(Moderator, WebsiteAdmin)



