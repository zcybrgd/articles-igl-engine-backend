# from rest_framework import status
# from rest_framework.test import APITestCase
# from django.urls import reverse
# from social_core.pipeline import user
# from django.test import TestCase, Client
# from requests import request
# from rest_framework import status
# import json
# from Users.models import Admin,user
# from django.contrib.auth.models import User, Group
# from Users.models import Moderator
# from rest_framework.response import Response

# class UserAPITest(APITestCase):
#     def test_signup(self):
#         url ='http://127.0.0.1:8000/us/signup'  # Assuming you have a 'signup' URL configured in your project

#         data = {
#             'userName': 'Maroumarou',
#             'password': 'tp@igl@20',
#             'firstName': 'MAROU',
#             'familyName': 'DJ',
#             'email': 'MAROUdJ@gmail.com'
#         }

#         response = self.client.post(url, data, format='json')
        
        
#         self.assertEqual(response.status_code, 200)
          
      

#     def test_signup_failed(self):
#         url ='http://127.0.0.1:8000/us/signup'  # Assuming you have a 'signup' URL configured in your project

#         data = {
#             'userName': 'Maroumarou',
#             'password': '',
#             'firstName': 'MAROU',
#             'familyName': 'DJ',
#             'email': 'MAROUdJ@gmail.com'
#         }

#         response = self.client.post(url, data, format='json')
        
        
#         self.assertEqual(response.status_code,status.HTTP_400_BAD_REQUEST)



from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from .models import NonUserToken , Admin, user,Moderator
from .views import make_password

class AddModAPITest(TestCase):
    
     def setUp(self):
        self.user = user.objects.create(userName='admin', password='admin',role='Administrator')
        self.admin= Admin.objects.create(id='1',userId=self.user)
        self.token = NonUserToken.objects.create(user=self.user)
        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
    
     def test_add_mod_authenticated_admin(self):
        
           
        data = {
         'userName': 'nehghw_mod',
         'password': 'mjgjodpass',
         'familyName': 'Dffoe',
         'firstName' : 'hghg',
         'familyName' : 'hghg',
         'email': 'jffohn.doe@example.com'
         }

#     #     # Make a POST request to add a new moderator
        response = self.client.post('http://127.0.0.1:8000/us/mod/add', data)
        response_json = response.json()
        self.assertIn('Mod added succesfully!!', response_json.keys())

        self.assertEqual(response.status_code, status.HTTP_200_OK)


     

     def test_add_mod_existing_user(self):
    # Create an existing moderator
        existing_mod = Moderator.objects.create(
            adminId=self.admin,
            userId=user.objects.create(userName='existing_mod', password='existing_mod_pass', role='Moderator'),
            userName='existing_mod',
            firstName='Jane',
            familyName='Doe',
            email='jane.doe@example.com',
            password=make_password('existing_mod_pass')
        )

        data = {
            'userName': 'existing_mod',
            'password': 'new_mod_pass',
            'role': 'Moderator',
            'firstName': 'John',
            'familyName': 'Doe',
            'email': 'john.doe@example.com'
        }

        response = self.client.post('/us/mod/add', data)

        response_json = response.json()
        self.assertIn('Username already exists. Please choose a different username.', response_json['error'])



     def test_add_mod_user_not_authenticated(self):
        # Ensure the user is not authenticated  # Remove authentication credentials
        self.client.logout()
        data = {
            'userName': 'new_mod',
            'password': 'new_mod_pass',
            'role': 'Moderator',
            'firstName': 'John',
            'familyName': 'Doe',
            'email': 'john.doe@example.com'
        }

        response = self.client.post('/us/mod/add', data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        response_json = response.json()
        
         


     def test_add_mod_admin_user_doesnt_exist(self):
                # Remove the admin user from the database
                self.admin.delete()

                data = {
                    'userName': 'new_mod',
                    'password': 'new_mod_pass',
                    'role': 'Moderator',
                    'firstName': 'John',
                    'familyName': 'Doe',
                    'email': 'john.doe@example.com'
                }

                response = self.client.post('/us/mod/add', data)

                
                response_json = response.json()
                self.assertIn("the admin user doesn't exist", response_json['error'])


     def test_add_mod_user_not_administrator(self):
                # Create a non-admin user
                non_admin_user = user.objects.create(userName='non_admin', password='non_admin_pass', role='Moderator')
                self.client.credentials(HTTP_AUTHORIZATION='Token ' + NonUserToken.objects.create(user=non_admin_user).key)

                data = {
                    'userName': 'new_mod',
                    'password': 'new_mod_pass',
                    'role': 'Moderator',
                    'firstName': 'John',
                    'familyName': 'Doe',
                    'email': 'john.doe@example.com'
                }

                response = self.client.post('/us/mod/add', data)

               
                response_json = response.json()
                self.assertIn("the user is not an administrator", response_json['error'])





class ModifyModViewTest(TestCase):

    def setUp(self):
        # Create an admin user
        self.user = user.objects.create(userName='admin', password='admin',role='Administrator')
        self.admin= Admin.objects.create(id='1',userId=self.user)
        self.token = NonUserToken.objects.create(user=self.user)
        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
     
        self.mod = Moderator.objects.create(
            adminId=self.admin,
            userId=user.objects.create(userName='existing_mod', password='existing_mod_pass', role='Moderator'),
            userName='existing_mod',
            firstName='Jane',
            familyName='Doe',
            email='jane.doe@example.com',
            password=make_password('existing_mod_pass')
        )
         
        # Create a moderator for modification
         
    def test_modify_mod(self):
    # Set client credentials to self.client.credentials()
     data = {
            'userName': 'new_mod_username',
            'password': 'new_mod_password',
            'firstName': 'NewJane',
            'familyName': 'NewDoe',
            'email': 'new.jane.doe@example.com'
        }

     response = self.client.put(f'/us/mod/modify/{self.mod.pk}', data)
     self.assertEqual(response.status_code, status.HTTP_200_OK)
     response_json = response.json()
     self.assertIn("Mod modified succesfully!!", response.content.decode())


    def test_add_mod_admin_user_doesnt_exist(self):
                # Remove the admin user from the database
     self.admin.delete()

     data = {
                    'userName': 'new_mod',
                    'password': 'new_mod_pass',
                    'role': 'Moderator',
                    'firstName': 'John',
                    'familyName': 'Doe',
                    'email': 'john.doe@example.com'
                }

     response = self.client.put(f'/us/mod/modify/{self.mod.pk}', data)
     self.assertEqual(response.status_code, status.HTTP_200_OK)
     response_json = response.json()
     self.assertIn("the admin user doesn't exist", response.content.decode())

    def test_modify_mod_mod_doesnt_exist(self):
      data = {
                    'userName': 'new_mod',
                    'password': 'new_mod_pass',
                    'firstName': 'John',
                    'familyName': 'Doe',
                    'email': 'john.doe@example.com'
                }

      response = self.client.put(f'/us/mod/modify/99', data, format='json')
      response_json = response.json()
      self.assertIn("the moderator doesn't exist", response.content.decode())
  
    def test_modify_mod_unauthorized_action(self):
        # Create a non-admin user
        
        self.user = user.objects.create(userName='admin2', password='admin2',role='Administrator')
        self.admin= Admin.objects.create(id='2',userId=self.user)
        self.token = NonUserToken.objects.create(user=self.user)
        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
     
        
         
        data = {
            'userName': 'new_mod_username',
            'password': 'new_mod_password',
            'firstName': 'NewJane',
            'familyName': 'NewDoe',
            'email': 'new.jane.doe@example.com'
        }

        response = self.client.put(f'/us/mod/modify/{self.mod.pk}', data)
        response_json = response.json()
        self.assertIn("This is an unauthorized action", response_json['error'])


    def test_modify_mod_user_not_administrator(self):
                # Create a non-admin user
     non_admin_user = user.objects.create(userName='non_admin', password='non_admin_pass', role='Moderator')
     self.client.credentials(HTTP_AUTHORIZATION='Token ' + NonUserToken.objects.create(user=non_admin_user).key)

     data = {
                    'userName': 'new_mod',
                    'password': 'new_mod_pass',
                    'role': 'Moderator',
                    'firstName': 'John',
                    'familyName': 'Doe',
                    'email': 'john.doe@example.com'
                }

     response = self.client.put(f'/us/mod/modify/{self.mod.pk}', data)
     response_json = response.json()
     self.assertIn("the user is not an administrator", response_json['error'])


      

    #   print(response.content)
    #   self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    #   response_json = response.json()
    #   self.assertIn("User non authenticated", response_json['error'])
   
#     def test_modify_mod_unauthenticated(self):
#     # Set client credentials to simulate an unauthenticated user
#      self.client.credentials()
#      data = {
#             'userName': 'new_mod_username',
#             'password': 'new_mod_password',
#             'firstName': 'NewJane',
#             'familyName': 'NewDoe',
#             'email': 'new.jane.doe@example.com'
#         }

#      response = self.client.put(f'/us/mod/modify/{self.mod.pk}', data)
#      self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
#      response_json = response.json()
#      self.assertIn("Mod modified succesfully!!", response.content.decode())
#     #   print(response.content)
#     #   self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
#     #   response_json = response.json()
#     #   self.assertIn("User non authenticated", response_json['error'])
   
