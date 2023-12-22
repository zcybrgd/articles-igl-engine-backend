from django.contrib import admin
from .models import Moderator


class WebsiteAdmin(admin.ModelAdmin):
    fields = ['userName', 'firstName', 'familyName', 'email', 'password', 'imgUrl']
    list_display = ['userName', 'email']


admin.site.register(Moderator, WebsiteAdmin)


