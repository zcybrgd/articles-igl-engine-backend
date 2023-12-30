import binascii
import os
from django.contrib.postgres.fields import ArrayField
from django.db import models
from rest_framework.authtoken.models import Token as BaseToken
from django.utils.translation import gettext_lazy as _


MAX_CHAR_LENGTH = 110  # constant to make the lengths of chars more maintainable


class user(models.Model):  # the common and important attributes that the 3 types of users have
    userName = models.CharField(max_length=MAX_CHAR_LENGTH, unique=True)
    password = models.CharField(max_length=MAX_CHAR_LENGTH)
    role = models.CharField(max_length=MAX_CHAR_LENGTH)
    is_active = models.BooleanField(_('active'),default=True,)
    is_authenticated = models.BooleanField(default=True)


#represents the admin in our database , he controls the Moderator model
class Admin(models.Model):
    id = models.IntegerField(primary_key=True)
    userId = models.OneToOneField(
        user,
        on_delete=models.CASCADE,
        blank=True,
        null=True
    )# to link the admin to its user instance


class Moderator(models.Model):
    userId = models.OneToOneField(
        user,
        on_delete=models.CASCADE,
        blank=True,
        null=True
    )
    adminId = models.ForeignKey(Admin, on_delete=models.CASCADE, blank=True, null=True)
    userName = models.CharField(max_length=MAX_CHAR_LENGTH, unique=True)
    firstName = models.CharField(max_length=MAX_CHAR_LENGTH)
    familyName = models.CharField(max_length=MAX_CHAR_LENGTH)
    email = models.CharField(max_length=MAX_CHAR_LENGTH)
    password = models.CharField(max_length=MAX_CHAR_LENGTH)
    profile_picture = models.ImageField(upload_to='profile_pics', null=True, blank=True, default='media/profile_pics/default_profile_pic.jpg')
    edit_count = models.IntegerField(default=0)  # New field to store edit count

    def __str__(self):
        return self.userName

#the client is the main user of our website , he's the one who searches for articles , reads them , save them to favorites and so on
class client(models.Model):
    userId = models.OneToOneField(
        user,
        on_delete=models.CASCADE,
        blank=True,
        null=True
    )  # to link the client to its user instance
    userName = models.CharField(max_length=MAX_CHAR_LENGTH, default=" ", unique=True)
    firstName = models.CharField(max_length=MAX_CHAR_LENGTH)
    familyName = models.CharField(max_length=MAX_CHAR_LENGTH)
    email = models.CharField(max_length=MAX_CHAR_LENGTH)
    password = models.CharField(max_length=MAX_CHAR_LENGTH, default=" ")
    profile_picture = models.ImageField(upload_to='media/profile_pics', null=True, blank=True, default='media/profile_pics/')
    favorite_articles = ArrayField(models.CharField(max_length=MAX_CHAR_LENGTH, blank=True), default=list)


#The token model that we used to replace the token model defined in the User's auth app
class NonUserToken(BaseToken):
    key = models.CharField(_("Key"), max_length=40, primary_key=True)
    user = models.OneToOneField(
        user, related_name='auth_token',
        on_delete=models.CASCADE, verbose_name=_("user")
    )
    created = models.DateTimeField(_("Created"), auto_now_add=True)

    class Meta:
        verbose_name = _("Token")
        verbose_name_plural = _("Tokens")

    def save(self, *args, **kwargs):
        if not self.key:
            self.key = self.generate_key()
        return super().save(*args, **kwargs)

    @classmethod
    def generate_key(cls):
        return binascii.hexlify(os.urandom(20)).decode()

    def __str__(self):
        return self.key
