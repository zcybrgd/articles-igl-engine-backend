from django.http import HttpResponse, JsonResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework import permissions
from django.shortcuts import get_object_or_404
from .serializers import UserSerializer, ClientSerializer, AdminSerializer, ModeratorSerializer
from .models import user, client, Token, Admin, Moderator
from django.contrib.auth.hashers import make_password


@api_view(['POST'])
@permission_classes((permissions.AllowAny,))
def signup(request):
    serializer = ClientSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        actualClient = client.objects.get(userName=request.data['userName'])
        actualClient.password = make_password(request.data['password'])
        userClient = user(userName=actualClient.userName, password=actualClient.password, role='Client')
        userClient.save()
        actualClient.userId = userClient
        actualClient.save()
        token = Token.objects.create(user=userClient)
        return Response({'token': token.key, 'user': serializer.data})
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def login(request):
    userClient = get_object_or_404(user, userName=request.data['userName'])
    if not user.check_password(request.data['password']):
        return Response("missing user", status=status.HTTP_404_NOT_FOUND)
    token, created = Token.objects.get_or_create(user=userClient)
    serializer = UserSerializer(user)
    return Response({'token': token.key, 'user': serializer.data})


def delete_user(request, id):
    try:
        userTodel = user.objects.get(pk=id)
    except user.DoesNotExist:
        return HttpResponse(status=status.HTTP_404_NOT_FOUND)
    userTodel.delete()
    return HttpResponse(status=status.HTTP_204_NO_CONTENT)

@permission_classes((permissions.AllowAny,))
def delete_client(request, id):
    try:
        clientTodel = client.objects.get(pk=id)
    except client.DoesNotExist:
        return HttpResponse(status=status.HTTP_404_NOT_FOUND)
    clientTodel.delete()
    return HttpResponse(status=status.HTTP_204_NO_CONTENT)


def users_list(request):
    users = user.objects.all()  # fetch the moderators from db
    response = UserSerializer(users, many=True)  # turning all of them into json
    return JsonResponse({"users": response.data})

@permission_classes((permissions.AllowAny,))
def clients_list(request):
    clients = client.objects.all()  # fetch the moderators from db
    response = ClientSerializer(clients, many=True)  # turning all of them into json
    return JsonResponse({"users": response.data})


def admins_list(request):
    admins = Admin.objects.all()  # fetch the moderators from db
    response = AdminSerializer(admins, many=True)  # turning all of them into json
    return JsonResponse({"admins": response.data})


# getting the list of moderators
def mods_list(request):
    mods = Moderator.objects.all()  # fetch the moderators from db
    response = ModeratorSerializer(mods, many=True)  # turning all of them into json
    return JsonResponse({"mods": response.data})  # returning the response while setting safe to false to allow non dict objects to be serialized

