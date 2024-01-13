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
        response = self.client.post('http://127.0.0.1:8000/us/mod/add', data)
        response_json = response.json()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('Mod added succesfully!!', response_json.keys())

        


     

     def test_add_mod_existing_moderator(self):
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
        # I couldn't get the custom response 
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



     def tearDown(self):
        # Clean up your test data
        Moderator.objects.all().delete()
        Admin.objects.all().delete()
        user.objects.all().delete()
        NonUserToken.objects.all().delete()

class ModifyModViewTest(TestCase):

    def setUp(self):
        # Create an admin user and the mod 
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
         
         
         
    def test_modify_mod_succeful(self):
   
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


    def test_modify_mod_admin_user_doesnt_exist(self):
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
       #we can enter a wrong id here it is 99
      response = self.client.put(f'/us/mod/modify/99', data, format='json')
      response_json = response.json()
      self.assertIn("the moderator doesn't exist", response.content.decode())
  
    def test_modify_mod_unauthorized_action(self):
        # login for another  admin not the one who created the moderator 
        
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


       

    def test_modify_mod_unauthenticated(self):
    # Set client credentials to simulate an unauthenticated user
     self.client.credentials()
     data = {
            'userName': 'new_mod_username',
            'password': 'new_mod_password',
            'firstName': 'NewJane',
            'familyName': 'NewDoe',
            'email': 'new.jane.doe@example.com'
        }
     #here I couldn't get the custom response 
     response = self.client.put(f'/us/mod/modify/{self.mod.pk}', data)
     self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
     response_json = response.json()
   
#I am not sure if the teardow is down that way
    def tearDown(self):
        # Clean up your test data
        Moderator.objects.all().delete()
        Admin.objects.all().delete()
        user.objects.all().delete()
        NonUserToken.objects.all().delete()


class DeleteModViewTest(TestCase):

    def setUp(self):
        # Create an admin user
        self.admin_user = user.objects.create(userName='admin', password='admin', role='Administrator')
        self.admin = Admin.objects.create(id='1', userId=self.admin_user)
        self.token = NonUserToken.objects.create(user=self.admin_user)
        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)

        # Create a moderator for deletion
        self.mod = Moderator.objects.create(
            adminId=self.admin,
            userId=user.objects.create(userName='mod_to_delete', password='mod_pass', role='Moderator'),
            userName='mod_to_delete',
            firstName='John',
            familyName='Doe',
            email='john.doe@example.com',
            password=make_password('mod_pass')
        )

    def test_delete_mod_successful(self):
        response = self.client.delete(f'/us/mod/delete/{self.mod.pk}')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_json = response.json()
        self.assertIn("Mod deleted successfully!!", response_json[0])

    def test_delete_mod_non_authenticated_user(self):
        self.client.logout()
        #same here I couldn't get the custom answer 
        response = self.client.delete(f'/us/mod/delete/{self.mod.pk}')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        # response_json = response.json()
        # self.assertIn("User non authenticated", response_json[0])

    def test_delete_mod_admin_user_doesnt_exist(self):
        #delete the admin 
        self.admin.delete()
        response = self.client.delete(f'/us/mod/delete/{self.mod.pk}')
        response_json = response.json()
        self.assertIn("the admin user doesn't exist", response_json['error'])

    def test_delete_mod_moderator_doesnt_exist(self):
        #the id doesn't exist 99
        response = self.client.delete('/us/mod/delete/99')
        response_json = response.json()
        self.assertIn("the moderator doesn't exist", response_json['error'])

    def test_delete_mod_unauthorized_action(self):
        #login for a new admin not the one who created the moderator 
        self.user = user.objects.create(userName='admin2', password='admin2',role='Administrator')
        self.admin= Admin.objects.create(id='2',userId=self.user)
        self.token = NonUserToken.objects.create(user=self.user)
        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        response = self.client.delete(f'/us/mod/delete/{self.mod.pk}')
        
        response_json = response.json()
        self.assertIn("This is an unauthorized action", response_json['error'])

    
    def test_delete_mod_user_not_administrator(self):
        # Create a non-admin user
        non_admin_user = user.objects.create(userName='non_admin', password='non_admin_pass', role='Moderator')
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + NonUserToken.objects.create(user=non_admin_user).key)

        response = self.client.delete(f'/us/mod/delete/{self.mod.pk}')
        
        response_json = response.json()
        self.assertIn("the user is not an administrator", response_json['error'])

    def tearDown(self):
        # Clean up your test data
        Moderator.objects.all().delete()
        Admin.objects.all().delete()
        user.objects.all().delete()
        NonUserToken.objects.all().delete()
        