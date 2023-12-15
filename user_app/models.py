from django.db import models

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




