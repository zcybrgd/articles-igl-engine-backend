import email

from django.http import JsonResponse, HttpResponse
from django.shortcuts import render
from rest_framework import status
from rest_framework.decorators import permission_classes, api_view
from rest_framework.response import Response

from . import admin
from .models import Moderator, user, Admin
from .serializers import ModeratorSerializer, UserSerializer, AdminSerializer


def home(request):
    return render(request, 'home.html')


def users_list(request):
    users = user.objects.all()  # fetch the moderators from db
    response = UserSerializer(users, many=True)  # turning all of them into json
    return JsonResponse({"users": response.data})

def admin_list(request):
    admins = Admin.objects.all()  # fetch the moderators from db
    response = AdminSerializer(admins, many=True)  # turning all of them into json
    return JsonResponse({"admins": response.data})


# getting the list of moderators
#@csrf_exempt
def mods_list(request):
    mods = Moderator.objects.all()  # fetch the moderators from db
    response = ModeratorSerializer(mods, many=True)  # turning all of them into json
    return JsonResponse({"mods": response.data})  # returning the response while setting safe to false to allow non dict objects to be serialized


#@csrf_exempt
def delete_user(request, id):
    try:
        userTodel = user.objects.get(pk=id)
    except user.DoesNotExist:
        return HttpResponse(status=status.HTTP_404_NOT_FOUND)
    userTodel.delete()
    return HttpResponse(status=status.HTTP_204_NO_CONTENT)


def delete_mod(request, id):
    try:
        modToDelete = Moderator.objects.get(pk=id)
    except Moderator.DoesNotExist:
        return HttpResponse(status=status.HTTP_404_NOT_FOUND)
    except user.DoesNotExist:
        return HttpResponse(status=status.HTTP_404_NOT_FOUND)
    modToDelete.delete()
    return HttpResponse(status=status.HTTP_204_NO_CONTENT)

