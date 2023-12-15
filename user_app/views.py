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


@api_view(['POST']) #adding a mod to the list of moderators
def add_mod(userName, firstName=None, familyName=None, password=None, imgUrl=None):
    user = UserSerializer(data={'userName': userName, 'firstName': firstName, 'familyName':familyName, 'email':email, 'password':password, 'role':'moderator', 'imgUrl':imgUrl}) #to take his user profile info
    if user.is_valid():
        user.save()
        mod = ModeratorSerializer(data={user.id, admin.id}) #to create his mod profile
        mod.save()
        return JsonResponse({"message": "Moderator added successfully"}, status=status.HTTP_201_CREATED)
    return Response(user.errors, status=status.HTTP_400_BAD_REQUEST)

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


def modify_mod(request,id):
    try:
        modToModify = Moderator.objects.get(pk=id)
    except Moderator.DoesNotExist:
        return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
    serializer = ModeratorSerializer(modToModify, data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response({"message": "User modified successfully"}, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
