import crum
from django.contrib.auth.hashers import make_password
from django.db.models.signals import pre_save, post_delete, post_save
from django.dispatch import receiver

from Users.models import Moderator, user, Admin


@receiver(pre_save, sender=Moderator)#before saving a moderator , to link it to its user profile and the admin that created it
def preSave_mod(sender, instance, **kwargs):
    instanceMod = Moderator.objects.filter(userName=instance.userName)
    if instanceMod.count() == 0:
        instance.password = make_password(instance.password)
        userInstance= user(userName=instance.userName, password=instance.password, role='Moderator')#creating user of the mode instance
        userInstance.save()
        instance.userId = userInstance
        admin = crum.get_current_user() #to get the instance of the actual active admin
        admin_bdd, created = Admin.objects.get_or_create(id=admin.id)#to create it in our own bdd if not already created
        if created:
            userAdmin = user(userName=admin.username, password=admin.password, role='Administrator')#create the user instance linked to our admin
            userAdmin.save()
            Admin.objects.filter(id=admin.id).update(userId=userAdmin.pk)#to give our bdd admin the id of the actual admin
        instance.adminId = admin_bdd
        admin_bdd.created_moderators.add(instance.userId)
    else:
        instanceMod = Moderator.objects.get(userName=instance.userName)
        if not(instanceMod.password == make_password(instance.password)):
            instance.password = make_password(instance.password)
        user.objects.filter(pk=instance.userId.pk).update(userName=instance.userName, password=instance.password)


@receiver(post_delete, sender=Moderator)
def delete_mod(sender, instance, **kwargs):
    admin = crum.get_current_user() #to get the instance of the actual active admin
    admin_bdd = Admin.objects.get(id=admin.id)
    #if admin.id == instance.adminId.id: #TO DO!!! i wanted to check if the one who wants to delete the mod is the admin who created it (we can hide the button on the front but we have to know if we need to do it in the backend too
    userInstance = user.objects.get(pk=instance.userId.pk)
    userInstance.delete()
    admin_bdd.created_moderators.remove(instance.userId)

