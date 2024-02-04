"""
This module contains API views and functionalities for user authentication, user settings, moderator manipulation, administrator statistics, and handling contact form submissions.

It includes functionalities for user signup, login, modifying client settings, adding and modifying moderators, retrieving moderator information, retrieving administrator statistics, handling contact form submissions, and retrieving contact messages.

The module provides API endpoints for these functionalities, with appropriate request methods and expected parameters.

"""
from django.http import JsonResponse, Http404
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework import permissions
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from .serializers import UserSerializer, ClientSerializer, ModeratorSerializer, ContactSerializer
from .models import user, client, Admin, Moderator, NonUserToken, contact
from django.contrib.auth.hashers import make_password, check_password
from django.contrib.auth import update_session_auth_hash




@api_view(['POST'])
@permission_classes((permissions.AllowAny,))
def signup(request):
    """
        Register a client into the database along with its user instance and create its token.

        This API expects a POST request with the following parameters:
        - userName: The unique username for the client.
        - firstName, familyName, profile_picture and e-mail
        - password: The password for the client's account.

        Returns:
        - If the registration is successful, it returns a JSON response with a token.
        - If the provided username already exists, it returns an error message.
        - If the provided data is invalid, it returns a 400 Bad Request error with validation errors.
        """
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
    """
        Log in a client or moderator.

        This API expects a POST request with the following parameters:
        - userName: The username of the user trying to log in.
        - password: The password of the user trying to log in.

        Returns:
        - If the login is successful, it returns a JSON response with a token and user details.
        - If the provided username does not exist, it returns an error message.
        - If the provided password is incorrect, it returns an error message.
        """
    # check if username exists in the request
    if 'userName' not in request.data:
        return Response({'error': "missing username"})

    # check if password exists in the request
    if 'password' not in request.data:
        return Response({'error': "missing password"})

    try:
        # here we are going to retrieve the user
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

@api_view(['GET'])
def client_login(request, id):
    """
            Warning, this is not the login view for the client, it's just used to retrieve additional client infomation to give
            the client the option to modify them in the profile settings (UI)
            Retrieve client details by ID. needed for the Profile Settings by the user
            This API expects a GET request with the client's ID.
            Returns:
            - If the client exists, it returns a JSON response with the client's details.
            - If the client does not exist, it returns an error message.
            """
    try:
        userlogin= user.objects.get(pk=id)
        clientlogin = client.objects.get(userId=userlogin)
    except user.DoesNotExist:
        return Response({'error': "the user doesn't exist "})
    except client.DoesNotExist:
        return JsonResponse({"client": "this is not a client"})
    response = ClientSerializer(clientlogin)
    return JsonResponse({"client": response.data})


@api_view(['PUT'])
def modify_client(request):
    """
        Modify client information except the password. as it is modified only in the settings

        This API expects a PUT request with the updated client data.

        Returns:
        - If the modification is successful, it returns a JSON response with the updated client data.
        - If the user is not authenticated or the client does not exist, it returns an error message.
        """
    connected = request.user  # to get the instance of the actual active client
    if connected.id is None:
        return Response({'error': "User non authenticated"})
    try:
        client_connect = client.objects.get(userId=connected)
    except client.DoesNotExist:
        return Response({'error': "the client doesn't exist "})
    client.objects.filter(pk=client_connect.id).update(**request.data)
    instanceClient = client.objects.get(pk=client_connect.id)
    user.objects.filter(pk=connected.id).update(userName=instanceClient.userName)  # to update the user instance of the client too
    updated_client = ClientSerializer(instanceClient)
    return Response({"data": updated_client.data})


@authentication_classes([])
@permission_classes([])
class modManipulation(APIView):
    """
        API views for moderator manipulation. Done only by the administrator
    """
    # api to add a moderator , the user must be an administrator
    @api_view(['POST'])
    def add_mod(request):
        """
                Add a new moderator.
                This API expects a POST request with the moderator's information.

                Returns:
                - If the moderator is added successfully, it returns a JSON response with the moderator data.
                - If the user is not an administrator or the username already exists, it returns an error message.
        """
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
        """
           Modify a moderator's information.

           This API expects a PUT request with the updated moderator data.

           Parameters:
           - id: The ID of the moderator to be modified.

           Returns:
           - If the modification is successful, it returns a JSON response with the updated moderator data.
           - If the user is not authenticated, the moderator doesn't exist, or the user is not authorized, it returns an error message.
           """
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
        """
            Delete a moderator.

            This API expects a DELETE request with the ID of the moderator to be deleted.

            Parameters:
            - id: The ID of the moderator to be deleted.

            Returns:
            - If the deletion is successful, it returns a JSON response indicating successful deletion.
            - If the user is not authenticated, the moderator doesn't exist, or the user is not authorized, it returns an error message.
            """

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
        """
           Retrieve all moderators created by the current administrator.

           This API expects a GET request.

           Returns:
           - A JSON response containing all moderators created by the current administrator.
           - If the user is not authenticated or is not an administrator, it returns an error message.
           """
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
    """
        API views for administrator statistics.
        To be displayed in the administrator's dashboard
    """
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
        """
           Retrieve the total number of validated articles by moderators under the current administrator.

           This API expects a GET request.

           Returns:
           - A JSON response containing the total number of validated articles.
           - If the user is not authenticated or is not an administrator, it returns an error message.
           """
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
        """
            Retrieve the total number of modified articles by moderators under the current administrator.

            This API expects a GET request.

            Returns:
            - A JSON response containing the total number of modified articles.
            - If the user is not authenticated or is not an administrator, it returns an error message.
            """
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
        """
           Retrieve the total number of moderators added by the current administrator.

           This API expects a GET request.

           Returns:
           - A JSON response containing the total number of moderators added.
           - If the user is not authenticated or is not an administrator, it returns an error message.
           """

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
        """
            Retrieve the total number of moderators deleted by the current administrator.

            This API expects a GET request.

            Returns:
            - A JSON response containing the total number of moderators deleted.
            - If the user is not authenticated or is not an administrator, it returns an error message.
            """
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
        """
            Retrieve the total number of moderators in the system.

            This API expects a GET request.

            Returns:
            - A JSON response containing the total number of moderators.
            - If the user is not authenticated or is not an administrator, it returns an error message.
            """
        connected = request.user
        if connected.id == None:
            return Response({'error': "User non authenticated"})
        if connected.role == "Administrator":
            mods = Moderator.objects.all().count()  # fetch all the moderators contained in the db
            return JsonResponse({"total_mods": mods})
        else:
            return Response({'error': "the user is not an administrator "})





@api_view(['POST'])
@permission_classes((permissions.AllowAny,))
def contactInfo(request):
    """
        Handle contact form submission.

        The contact form is present in the welcome page

        This API expects a POST request with the contact form data.

        Returns:
        - If the submission is successful, it returns a JSON response with a success message.
        - If there's an error in the submission, it returns an error message.
        """
    serializer = ContactSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return JsonResponse({'message': 'Sent successfully ! Thank you for your feedback'},status=status.HTTP_201_CREATED)
    return Response({'error': 'An Error occured'}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes((permissions.AllowAny,))
def contactsMsgs(request):
    """
        Retrieve all contact messages.

        This API expects a GET request.

        Returns:
        - A JSON response containing all contact messages.
        """
    contacts = contact.objects.all()  # fetch the messages from db
    response = ContactSerializer(contacts, many=True)  # turning all of them into json
    return JsonResponse({"contacts": response.data})

@authentication_classes([])
@permission_classes([])
class userSettings(APIView):
    """
       API views for user settings.

       This class provides endpoints for modifying user settings, specifically for clients.
       """
    @api_view(['PUT'])
    def modifyClient(request, id):
        """
                Modify client settings.

                This API expects a PUT request with the updated client data.

                Parameters:
                - id: The ID of the client to be modified.

                Returns:
                - If the modification is successful, it returns a JSON response with the updated client data.
                - If the user is not authenticated or is not a client, it returns an error message.
                """
        connected = request.user # to get the instance of the actual active user
        if connected.id is None:
            return JsonResponse({'error': "User not authenticated"})

        if connected.role == "Client":
            try:
                clientConnected = client.objects.get(userId=connected)
            except client.DoesNotExist:
                return JsonResponse({'error': "The client user doesn't exist "})

            currentPassword = request.data.get('current_password', None)
            newUsername = request.data.get('new_username', clientConnected.userName)
            newPassword = request.data.get('new_password', clientConnected.password)
            confirmNewPassword = request.data.get('confirmNewPassword', clientConnected.password)

            # Verify current password
            if not check_password(currentPassword, connected.password):
                return Response({'error': 'Incorrect current password'}, status=status.HTTP_400_BAD_REQUEST)

            if newPassword != confirmNewPassword:
                return JsonResponse({'error': 'New password and confirmation do not match'})

            # Update user Client fields
            if newUsername:
                connected.userName = newUsername
            if newPassword:
                connected.password = make_password(newPassword)

            connected.save()

            # Update the session auth hash to avoid logout after password change
            update_session_auth_hash(request, connected)

            # Apply the changes on the Client Serializer
            serializer = ClientSerializer(clientConnected)
            return JsonResponse({'message': 'Modifications applied successfully', 'data': serializer.data})

        return JsonResponse({'error': "User is not a client"})