from django.apps import AppConfig


class UsersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'Users'

    def ready(self):
        from django.contrib.auth.models import User
        from Users.models import Admin, user
        admins = User.objects.all()  # getting all the admins created using the createsuperuser command
        for ad in admins:
            adBdd, created = Admin.objects.get_or_create(id=ad.id)  # checking if the admin ad is in our db yet
            if created:  # if not , we create its user instance with role administrator
                userAdmin = user(userName=ad.username, password=ad.password, role='Administrator')
                userAdmin.save()
                Admin.objects.filter(id=adBdd.id).update(userId=userAdmin.pk)

