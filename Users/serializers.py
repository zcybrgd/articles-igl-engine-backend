from rest_framework import serializers
from .models import Moderator, user, Admin, client, contact


class ModeratorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Moderator
        fields = ['id', 'adminId', 'userId', 'userName', 'firstName', 'familyName', 'email', 'password', 'profile_picture','edit_count','delete_count', 'validate_count']


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = user
        fields = ['id', 'userName', 'password', 'role']


class AdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = Admin
        fields = ['id', 'userId', 'delete_mods']


class ClientSerializer(serializers.ModelSerializer):
    class Meta:
        model = client
        fields = ['id', 'userId', 'userName', 'firstName', 'familyName', 'email', 'password', 'profile_picture']


class ContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = contact
        fields = ['name', 'email', 'message']
