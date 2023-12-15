import crum
from django.db import models
from django.db.models.signals import pre_save
from django.dispatch import receiver

MAX_CHAR_LENGTH = 110  # constant to make the lengths of chars more maintainable


# Create your models here.
class user(models.Model):  # the common attributes that the 3 types of users have
    userName = models.CharField(max_length=MAX_CHAR_LENGTH)
    password = models.CharField(max_length=MAX_CHAR_LENGTH)
    role = models.CharField(max_length=MAX_CHAR_LENGTH)


class Admin(models.Model):
    id = models.IntegerField(primary_key=True)
    userId = models.OneToOneField(
        user,
        on_delete=models.CASCADE,
        blank=True,
        null=True
    )


class Moderator(models.Model):  # a moderator in our website is in charge of correcting extracted articles , validating and deleting them
    userId = models.OneToOneField(
        user,
        on_delete=models.CASCADE,
        blank=True,
        null=True
    )  # to link the moderator to its user attributes/profile
    adminId = models.ForeignKey(Admin, on_delete=models.CASCADE, blank=True, null=True)
    userName = models.CharField(max_length=MAX_CHAR_LENGTH)
    firstName = models.CharField(max_length=MAX_CHAR_LENGTH)
    familyName = models.CharField(max_length=MAX_CHAR_LENGTH)
    email = models.CharField(max_length=MAX_CHAR_LENGTH)
    password = models.CharField(max_length=MAX_CHAR_LENGTH)
    imgUrl = models.CharField(max_length=MAX_CHAR_LENGTH)


@receiver(pre_save, sender=Moderator)
def save_user(sender, instance, **kwargs):
    userInstance = user(userName=instance.userName, password=instance.password, role='Moderator')#creating user of the mode instance
    userInstance.save()
    instance.userId = userInstance
    admin = crum.get_current_user() #to get the instance of the actual active admin
    admin_bdd, created = Admin.objects.get_or_create(id=admin.id)#to create it in our own bdd if not already created
    if created:
        userAdmin = user(userName=admin.username, password=admin.password, role='Administrator')#create the user instance linked to our admin
        userAdmin.save()
        Admin.objects.filter(id=admin.id).update(userId=userAdmin.pk)#to give our bdd admin the id of the actual admin
    instance.adminId = admin_bdd
