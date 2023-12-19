from django.contrib.auth.hashers import UNUSABLE_PASSWORD_PREFIX, UNUSABLE_PASSWORD_SUFFIX_LENGTH, get_hasher
from django.contrib.auth.models import User
from django.db import models
from django.utils.crypto import get_random_string

MAX_CHAR_LENGTH = 110  # constant to make the lengths of chars more maintainable


# Create your models here.
class user(models.Model):  # the common and important attributes that the 3 types of users have
    userName = models.CharField(max_length=MAX_CHAR_LENGTH)
    password = models.CharField(max_length=MAX_CHAR_LENGTH)
    role = models.CharField(max_length=MAX_CHAR_LENGTH)

#represents the admin in our database , he controls the Moderator model
class Admin(models.Model):
    id = models.IntegerField(primary_key=True)
    userId = models.OneToOneField(
        user,
        on_delete=models.CASCADE,
        blank=True,
        null=True
    )# to link the admin to its user instance


class Moderator(models.Model):  # a moderator in our website is in charge of correcting extracted articles , validating and deleting them
    userId = models.OneToOneField(
        user,
        on_delete=models.CASCADE,
        blank=True,
        null=True
    )  # to link the moderator to its user instance
    adminId = models.ForeignKey(Admin, on_delete=models.CASCADE, blank=True, null=True)
    userName = models.CharField(max_length=MAX_CHAR_LENGTH)
    firstName = models.CharField(max_length=MAX_CHAR_LENGTH)
    familyName = models.CharField(max_length=MAX_CHAR_LENGTH)
    email = models.CharField(max_length=MAX_CHAR_LENGTH)
    password = models.CharField(max_length=MAX_CHAR_LENGTH)
    imgUrl = models.CharField(max_length=MAX_CHAR_LENGTH)


class client(models.Model):
    userId = models.OneToOneField(
        user,
        on_delete=models.CASCADE,
        blank=True,
        null=True
    )  # to link the client to its user instance
    userName = models.CharField(max_length=MAX_CHAR_LENGTH, default=" ")
    firstName = models.CharField(max_length=MAX_CHAR_LENGTH)
    familyName = models.CharField(max_length=MAX_CHAR_LENGTH)
    email = models.CharField(max_length=MAX_CHAR_LENGTH)
    password = models.CharField(max_length=MAX_CHAR_LENGTH, default=" ")
    imgUrl = models.CharField(max_length=MAX_CHAR_LENGTH)

    def set_password(raw_password):
        return User.set_password(raw_password)


    def make_password(password, salt=None, hasher="default"):
        if password is None:
            return UNUSABLE_PASSWORD_PREFIX + get_random_string(
                UNUSABLE_PASSWORD_SUFFIX_LENGTH
        )
        if not isinstance(password, (bytes, str)):
            raise TypeError(
            "Password must be a string or bytes, got %s." % type(password).__qualname__
        )
        hasher = get_hasher(hasher)
        salt = salt or hasher.salt()
        return hasher.encode(password, salt)

