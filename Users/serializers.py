from rest_framework import serializers
from .models import Moderator, user, Admin, client


class ModeratorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Moderator
        fields = ['id', 'adminId', 'userId', 'userName', 'firstName', 'familyName', 'email', 'password', 'profile_picture','edit_count']


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = user
        fields = ['id', 'userName', 'password', 'role']


class AdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = Admin
        fields = ['id', 'userId','created_moderators']


class ClientSerializer(serializers.ModelSerializer):
    class Meta:
        model = client
        fields = ['id', 'userId', 'userName', 'firstName', 'familyName', 'email', 'password', 'profile_picture']
