from django.http import HttpResponse, JsonResponse, Http404
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework import permissions
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from .serializers import UserSerializer, ClientSerializer, AdminSerializer, ModeratorSerializer
from .models import user, client, Admin, Moderator, NonUserToken
from django.contrib.auth.hashers import make_password, check_password


# this is an api to register a client into the db , alon with its user instance and creating its token
@api_view(['POST'])
@permission_classes((permissions.AllowAny,))
def signup(request):
    existing_user = client.objects.filter(userName=request.data.get('userName', ''))
    if existing_user.exists():
        return Response({'error': 'Username already exists. Please choose a different username.'})
    serializer = ClientSerializer(data=request.data)
    # the userName field must be unique , if not a message will appear telling the user to change it
    if serializer.is_valid():
        serializer.save()
        actualClient = client.objects.get(userName=request.data['userName'])
        actualClient.password = make_password(request.data['password'])  # hash the password provided by the user
        userClient = user(userName=actualClient.userName, password=actualClient.password,
                          role='Client')  # registering the user instance
        userClient.save()
        actualClient.userId = userClient  # linking the client to its user instance
        actualClient.save()
        token = NonUserToken.objects.create(user=userClient)  # creating its token
        return Response({'token': token.key})
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# this api is used to login both the client and moderator , the difference is in the role attribute in their user instance
@api_view(['POST'])
@permission_classes((permissions.AllowAny,))
def login(request):
    # check if username exists in the request
    if 'userName' not in request.data:
        return Response({'error': "missing username"})

    # check if password exists in the request
    if 'password' not in request.data:
        return Response({'error': "missing password"})

    try:
        # récuperer the user
        user_client = get_object_or_404(user, userName=request.data['userName'])
    except Http404:
        # if it doesnt exist
        return Response({'error': "username does not exist"})

    # check if the passowrd provided is correct
    if not check_password(request.data['password'], user_client.password):
        return Response({'error': "incorrect password"})
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
    return JsonResponse({
        "mods": response.data})  # returning the response while setting safe to false to allow non dict objects to be serialized


@authentication_classes([])
@permission_classes([])
class modManipulation(APIView):
    # api to add a moderator , the user must be an administrator
    @api_view(['POST'])
    def add_mod(request):
        connected = request.user  # extracting the current user instance
        if connected.id == None:
            return Response({'error':"User non authenticated"})
        if connected.role == "Administrator":
            existing_mod = Moderator.objects.filter(
                userName=request.data['userName'])  # to find if the username already exists
            if existing_mod.exists():
                return Response({'error': 'Username already exists. Please choose a different username.'})
            password = make_password(request.data['password'])  # hashing the password
            userInstance = user(userName=request.data['userName'], password=password,
                                role='Moderator')  # to create the user instance of the mod
            userInstance.save()
            try:
                admin_bdd = Admin.objects.get(userId=connected)  # to get the admin instance from the db and adding it to the mod as adminId
            except Admin.DoesNotExist:
                return Response({'error': "the admin user doesn't exist "})
            instanceMod = Moderator(adminId=admin_bdd, userId=userInstance, userName=request.data['userName'],
                                    firstName=request.data['firstName'], familyName=request.data['familyName'],
                                    email=request.data['email'], password=password)  # creating the moderator instance
            instanceMod.save()
            mod = ModeratorSerializer(instanceMod)
            return Response({"Mod added succesfully!!": mod.data})
        else:
            return Response({'error': "the user is not an administrator "})

    @api_view(['PUT'])
    def modify_mod(request, id):
        connected = request.user  # to get the instance of the actual active admin
        if connected.id == None:
            return Response({'error':"User non authenticated"})
        if connected.role == "Administrator":
            try:
                admin_connect = Admin.objects.get(userId=connected)
            except Admin.DoesNotExist:
                return Response({'error': "the admin user doesn't exist "})
            try:
                mod = Moderator.objects.get(pk=id)  # getting the mod instance based on the id in the url
            except Moderator.DoesNotExist:
                return Response({'error': "the moderator doesn't exist "})
            if mod.adminId == admin_connect:  # to check if the admin who created the mod is actually the onec currently connected
                Moderator.objects.filter(pk=id).update(**request.data)
                try:
                    instanceMod = Moderator.objects.get(
                        pk=id)  # to get the mod again after updating , and to check if the password didn't change , if changed we hash it again
                except Moderator.DoesNotExist:
                    return Response({'error': "the moderator doesn't exist "})
                if not (instanceMod.password == make_password(request.data['password'])):
                    instanceMod.password = make_password(request.data['password'])
                instanceMod.save()
                user.objects.filter(pk=instanceMod.userId.pk).update(userName=instanceMod.userName,
                                                                     password=instanceMod.password)  # to update the user instance of the mod too
                mod = ModeratorSerializer(instanceMod)
                return Response({"Mod modified succesfully!!": mod.data})
            else:
                return Response({'error': "This is an unauthorized action"})
        else:
            return Response({'error': "the user is not an administrator "})

    @api_view(['DELETE'])
    def delete_mod(request, id):
        connected = request.user  # to get the instance of the actual active admin
        if connected.id == None:
            return Response({'error': "User non authenticated"})
        if connected.role == "Administrator":
            try:
                admin_connect = Admin.objects.get(userId=connected)
            except Admin.DoesNotExist:
                return Response({'error': "the admin user doesn't exist "})
            try:
                mod = Moderator.objects.get(pk=id)  # getting the mod instance based on the id in the url
            except Moderator.DoesNotExist:
                return Response({'error': "the moderator doesn't exist "})
            if mod.adminId == admin_connect:  # to check if the admin who created the mod is actually the onec currently connected
                try:
                    userInstance = user.objects.get(pk=mod.userId.id) # to get the user instance of the mod the admin wants to delete
                except user.DoesNotExist:
                    return Response({'error': "the user instance doesn't exist "})
                userInstance.delete()  # the userId of the mod have a delete on cascade property , so if its user instance is deleted , it will be
                admin_connect.delete_mods = admin_connect.delete_mods+1
                admin_connect.save()
                return Response({"Moderator deleted succesfully!!"})
            else:
                return Response({'error': "This is an unauthorized action"})
        else:
            return Response({'error': "the user is not an administrator "})

    @api_view(['GET'])
    def display_mods(request):
        connected = request.user
        if connected.id == None:
            return Response({'error': "User non authenticated"})
        if connected.role == "Administrator":
            try:
                adminConnected = Admin.objects.get(userId=connected)
            except Admin.DoesNotExist:
                return Response({'error': "the admin user doesn't exist "})
            mods = Moderator.objects.filter(adminId=adminConnected)  # fetch the moderators from db such as they are created by this admin
            response = ModeratorSerializer(mods, many=True)  # turning all of them into json
            return JsonResponse({"mods": response.data})
        else:
            return Response({'error': "the user is not an administrator "})


@authentication_classes([])
@permission_classes([])
class adminStats(APIView):
    @api_view(['GET'])
    def deleted_articles(request):
        connected = request.user
        if connected.id == None: #the user is anonymous
            return Response({'error': "User non authenticated"})
        if connected.role == "Administrator":
            try:
                adminConnected = Admin.objects.get(userId=connected)
            except Admin.DoesNotExist:
                return Response({'error': "the admin user doesn't exist "})
            mods = Moderator.objects.filter(adminId=adminConnected)  # fetch the moderators from db such as they are created by this admin
            total_deleted = 0
            for mod in mods: # get the delete_count of each mod of the admin connected and sum them
                total_deleted = total_deleted+mod.delete_count
            return JsonResponse(
                {"deleted_articles": total_deleted})
        else:
            return Response({'error': "the user is not an administrator "})

    @api_view(['GET'])
    def validated_articles(request):
        connected = request.user
        if connected.id == None:
            return Response({'error': "User non authenticated"})
        if connected.role == "Administrator":
            try:
                adminConnected = Admin.objects.get(userId=connected)
            except Admin.DoesNotExist:
                return Response({'error': "the admin user doesn't exist "})
            mods = Moderator.objects.filter(adminId=adminConnected)  # fetch the moderators from db such as they are created by this admin
            total_validated = 0
            for mod in mods:  # get the validate_count of each mod of the admin connected and sum them
                total_validated = total_validated+mod.validate_count
            return JsonResponse(
                {"validated_articles": total_validated})
        else:
            return Response({'error': "the user is not an administrator "})

    @api_view(['GET'])
    def modified_articles(request):
        connected = request.user
        if connected.id == None:
            return Response({'error': "User non authenticated"})
        if connected.role == "Administrator":
            try:
                adminConnected = Admin.objects.get(userId=connected)
            except Admin.DoesNotExist:
                return Response({'error': "the admin user doesn't exist "})
            mods = Moderator.objects.filter(adminId=adminConnected)  # fetch the moderators from db such as they are created by this admin
            total_modified = 0
            for mod in mods:  # get the number of edits of each mod of the admin connected and sum them
                total_modified = total_modified+mod.edit_count
            return JsonResponse(
                {"modified_articles": total_modified})
        else:
            return Response({'error': "the user is not an administrator "})

    @api_view(['GET'])
    def added_mods(request):
        connected = request.user
        if connected.id == None:
            return Response({'error': "User non authenticated"})
        if connected.role == "Administrator":
            try:
                adminConnected = Admin.objects.get(userId=connected)
            except Admin.DoesNotExist:
                return Response({'error': "the admin user doesn't exist "})
            mods = Moderator.objects.filter(adminId=adminConnected).count()  # fetch the numbers of moderators that are created by this admin
            return JsonResponse({"added_mods": mods})
        else:
            return Response({'error': "the user is not an administrator "})

    @api_view(['GET'])
    def deleted_mods(request):
        connected = request.user
        if connected.id == None:
            return Response({'error': "User non authenticated"})
        if connected.role == "Administrator":
            try:
                adminConnected = Admin.objects.get(userId=connected)
            except Admin.DoesNotExist:
                return Response({'error': "the admin user doesn't exist "})
            mods = adminConnected.delete_mods  # fetch the number of mods deleted by this admin
            return JsonResponse({"deleted_mods": mods})
        else:
            return Response({'error': "the user is not an administrator "})

    @api_view(['GET'])
    def total_mods(request):
        connected = request.user
        if connected.id == None:
            return Response({'error': "User non authenticated"})
        if connected.role == "Administrator":
            mods = Moderator.objects.all().count()  # fetch all the moderators contained in the db
            return JsonResponse({"total_mods": mods})
        else:
            return Response({'error': "the user is not an administrator "})
