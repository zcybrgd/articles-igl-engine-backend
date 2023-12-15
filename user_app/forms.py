from django import forms
from user_app.models import Moderator


class ModeratorForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = Moderator
