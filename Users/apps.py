from django.apps import AppConfig
from django.db.models.signals import post_migrate


class UsersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'Users'

    def ready(self):
        pass


def create_initial_admins(sender, **kwargs):
    from django.contrib.auth.models import User
    from Users.models import Admin, user

    if sender.name == 'django.contrib.auth':
        admins = User.objects.all()
        for ad in admins:
            adBdd, created = Admin.objects.get_or_create(id=ad.id)
            if created:
                userAdmin = user(userName=ad.username, password=ad.password, role='Administrator')
                userAdmin.save()
                Admin.objects.filter(id=adBdd.id).update(userId=userAdmin.pk)


post_migrate.connect(create_initial_admins, sender=UsersConfig)
