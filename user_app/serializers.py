from rest_framework import serializers
from .models import Moderator, user, Admin


class ModeratorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Moderator
        fields = ['id', 'adminId', 'userId', 'userName', 'firstName', 'familyName', 'email', 'password', 'imgUrl']


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = user
        fields = ['id', 'userName', 'password', 'role']


class AdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = Admin
        fields = ['id', 'userId']

