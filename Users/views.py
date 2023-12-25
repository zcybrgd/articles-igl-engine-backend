from django.http import HttpResponse, JsonResponse, Http404
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework import permissions
from django.shortcuts import get_object_or_404
from .serializers import UserSerializer, ClientSerializer, AdminSerializer, ModeratorSerializer
from .models import user, client, NonUserToken, Admin, Moderator
from django.contrib.auth.hashers import make_password, check_password

#this is an api to register a client into the db , alon with its user instance and creating its token
@api_view(['POST'])
@permission_classes((permissions.AllowAny,))
def signup(request):
    existing_user = client.objects.filter(userName=request.data.get('userName', ''))

    if existing_user.exists():
        return Response({'error': 'Username already exists. Please choose a different username.'})
    serializer = ClientSerializer(data=request.data)
    #the userName field must be unique , if not a message will appear telling the user to change it
    if serializer.is_valid():
        serializer.save()
        actualClient = client.objects.get(userName=request.data['userName'])
        actualClient.password = make_password(request.data['password']) #hash the password provided by the user
        userClient = user(userName=actualClient.userName, password=actualClient.password, role='Client') #registering the user instance
        userClient.save()
        actualClient.userId = userClient #linking the client to its user instance
        actualClient.save()
        token = NonUserToken.objects.create(user=userClient) #creating its token
        return Response({'token': token.key})
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


#this api is used to login both the client and moderator , the difference is in the role attribute in their user instance
@api_view(['POST'])
@permission_classes((permissions.AllowAny,))
def login(request):
    #check if username exists in the request
    if 'userName' not in request.data:
        return Response({'error':"missing username"})

    #check if password exists in the request
    if 'password' not in request.data:
        return Response({'error':"missing password"})

    try:
        #récuperer the user
        user_client = get_object_or_404(user, userName=request.data['userName'])
    except Http404:
        #if it doesnt exist
        return Response({'error':"username does not exist"})

    #check if the passowrd provided is correct
    if not check_password(request.data['password'], user_client.password):
        return Response({'error':"incorrect password"})

    token, created = NonUserToken.objects.get_or_create(user=user_client)
    serializer = UserSerializer(user_client)
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
    users = user.objects.all()  # fetch the users from db
    response = UserSerializer(users, many=True)  # turning all of them into json
    return JsonResponse({"users": response.data})

@permission_classes((permissions.AllowAny,))
def clients_list(request):
    clients = client.objects.all()  # fetch the clients from db
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

